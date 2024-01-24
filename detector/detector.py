import numpy as np
import cv2
from cv2 import aruco
import copy
import os
import pathlib
from detector import sender
import math
from vreactable import VreactableApp

# ChAruco board configs
PATTERN = (5, 7)
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)

SQUARE_LENGTH = 1
MARKER_LENGTH = 0.85

CHARUCO_BOARD = aruco.CharucoBoard(
    size=PATTERN,
    squareLength=SQUARE_LENGTH,
    markerLength=MARKER_LENGTH,
    dictionary=ARUCO_DICT,
)
OBJ_POINTS = np.zeros((4, 3), np.float32)
OBJ_POINTS[0] = np.array([[-MARKER_LENGTH / 2.0, MARKER_LENGTH / 2.0, 0]], np.float32)
OBJ_POINTS[1] = np.array([[MARKER_LENGTH / 2.0, MARKER_LENGTH / 2.0, 0]], np.float32)
OBJ_POINTS[2] = np.array([[MARKER_LENGTH / 2.0, -MARKER_LENGTH / 2.0, 0]], np.float32)
OBJ_POINTS[3] = np.array([[-MARKER_LENGTH / 2.0, -MARKER_LENGTH / 2.0, 0]], np.float32)

isLastObjectGone = False


# wrap angle because in game the angle is from -180 to 180
def wrapAngle(angle):
    """
    Wrap an angle to the range -180 to 180 degrees.

    Args:
        angle (float): Input angle in degrees.

    Returns:
        float: Wrapped angle in the range -180 to 180 degrees.
    """
    wrapped_angle = (angle + 180) % 360

    if wrapped_angle > 180:
        wrapped_angle = wrapped_angle - 360
    return wrapped_angle


class CubeDetector:
    def __init__(self, app: VreactableApp, detect_callback):
        self.websocket = None
        self.app = app
        self.detect_callback = detect_callback
        pass

    def detect_arucos(self, calibFilePath: str, ip: str):
        with np.load(calibFilePath) as X:
            cameraMatrix, distCoeffs = [X[i] for i in ("cameraMatrix", "distCoeffs")]
        print("Calibration file is loaded...")
        self.websocket = sender.setup_websocket_client(ip)
        print("Websocket is set...")
        self.__run__(cameraMatrix, distCoeffs)

    # private
    def __run__(self, cameraMatrix, distCoeffs):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("error: cannot open camera")
            exit()

        print("Camera is found...")
        while cap.isOpened():
            isCaptured, frame = cap.read()

            if isCaptured:
                self.__detect_frame__(frame, cameraMatrix, distCoeffs)

            key = cv2.waitKey(math.floor(1000 / 30))
            if key == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()

    # private
    def __detect_frame__(self, frame, cameraMatrix, distCoeffs):
        global isLastObjectGone
        imageCopy = copy.copy(frame)
        detectorParams = aruco.DetectorParameters()
        detector = aruco.ArucoDetector(
            dictionary=ARUCO_DICT, detectorParams=detectorParams
        )

        gray = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2GRAY)
        markerCorners, markerIds, _ = detector.detectMarkers(gray)

        isFound = (markerIds is not None) and len(markerIds) > 0

        if isFound:
            markerCount = len(markerIds)
            aruco.drawDetectedMarkers(imageCopy, markerCorners, markerIds)
            cv2.putText(
                imageCopy,
                f"Markers found",
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1,
            )

            rotations = [None] * markerCount
            rvecs = [None] * markerCount
            tvecs = [None] * markerCount

            filteredMarkerIds = [-1] * 6
            filteredTvecs = [None] * 6
            filteredRvecs = [None] * 6
            filteredRotations = [np.array([360, 360, 360], np.float32)] * 6

            for i in range(markerCount):
                retval, rvecs[i], tvecs[i] = cv2.solvePnP(
                    OBJ_POINTS, markerCorners[i], cameraMatrix, distCoeffs
                )
                # Convert rotation vector to rotation matrix
                rot_mat, _ = cv2.Rodrigues(rvecs[i])

                proj_matrix = np.hstack((rot_mat, tvecs[i]))
                eulerAngles = cv2.decomposeProjectionMatrix(proj_matrix)[6]

                roll_degrees, pitch_degrees, yaw_degrees = eulerAngles

                roll_degrees = wrapAngle(roll_degrees[0])
                pitch_degrees = pitch_degrees[0]
                yaw_degrees = yaw_degrees[0]

                rotation = np.array(
                    [roll_degrees, pitch_degrees, yaw_degrees], np.float32
                )
                # filter by rotations so there will be only 1 marker on a box being detected
                cubeIndex = int(markerIds[i] / 6)
                # pitch diff with platform
                rollDiff = abs(rotation[0])
                pitchDiff = abs(rotation[1])
                if (
                    rollDiff < abs(filteredRotations[cubeIndex][0])
                    and pitchDiff < abs(filteredRotations[cubeIndex][1])
                    and rollDiff < 55
                    and pitchDiff < 55
                ):
                    filteredMarkerIds[cubeIndex] = markerIds[i]
                    filteredTvecs[cubeIndex] = tvecs[i]
                    filteredRvecs[cubeIndex] = rvecs[i]
                    filteredRotations[cubeIndex] = rotation

            for i in range(6):
                if filteredMarkerIds[i] != -1:
                    cv2.drawFrameAxes(
                        imageCopy,
                        cameraMatrix,
                        distCoeffs,
                        filteredRvecs[i],
                        filteredTvecs[i],
                        0.5,
                    )

            # post prcoess data
            for i in range(6):
                if filteredMarkerIds[i] > -1:
                    filteredTvecs[0] = 0 if self.app.var_lock_x else filteredTvecs[0][0]
                    filteredTvecs[1] = (
                        0 if self.app.var_lock_y else filteredTvecs[1][0] * -1
                    )
                    filteredTvecs[2] = 0 if self.app.var_lock_z else filteredTvecs[2][0]
                    filteredRotations[0] = (
                        0 if self.app.var_lock_roll else filteredRotations[0]
                    )
                    filteredRotations[1] = (
                        0 if self.app.var_lock_pitch else filteredRotations[1]
                    )
                    filteredRotations[2] = (
                        0 if self.app.var_lock_yaw else filteredRotations[2]
                    )

            # send data
            sender.send_object_data(
                self.websocket, filteredMarkerIds, filteredTvecs, filteredRotations
            )

            self.detect_callback(filteredMarkerIds, filteredTvecs, filteredRotations)
            isLastObjectGone = False

        else:
            if isLastObjectGone is False:
                sender.send_object_data(self.websocket, [], [], [])
                isLastObjectGone = True
            cv2.putText(
                imageCopy,
                f"Markers not found",
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1,
            )

        cv2.putText(
            imageCopy,
            f"Press Q to leave",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1,
        )

        cv2.imshow("detector", imageCopy)

        return markerCorners, markerIds
