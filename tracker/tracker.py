import numpy as np
import cv2
from cv2 import aruco
import copy
import os
import pathlib
from tracker.sender import Client
import math

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
    wrappedAngle = (angle + 180) % 360

    if wrappedAngle > 180:
        wrappedAngle = wrappedAngle - 360
    return wrappedAngle


class CubeTracker:
    def __init__(self, app, onTrack, onTrackingFinish, onTrackingFail):
        self.client = None
        self.app = app
        self.onTrack = onTrack
        self.onTrackingFinish = onTrackingFinish
        self.onTrackingFail = onTrackingFail
        self.forceTerminate = False
        pass
    
    def terminate(self):
        self.forceTerminate = True
        pass

    def startTrackingMarkers(self, calibFilePath: str, ip: str, cameraIndex: int):
        with np.load(calibFilePath) as X:
            cameraMatrix, distCoeffs = [X[i] for i in ("cameraMatrix", "distCoeffs")]
        print("Calibration file is loaded...")
        try:
            self.client = Client(ip)
            pass
        except Exception as e:
            self.onTrackingFail("Failed to setup Websocket. Please check whether the ip address is correct then try again.")
            raise e
        print("Websocket is set...")
        try:
            self.__run__(cameraMatrix, distCoeffs, cameraIndex)
            pass
        except Exception as e:
            self.onTrackingFail("Unknown error. Please check console to address the issue.")
            raise e

    # private
    def __run__(self, cameraMatrix, distCoeffs, cameraIndex):
        cap = cv2.VideoCapture(cameraIndex, cv2.CAP_DSHOW)

        if not cap.isOpened():
            print("error: cannot open camera")
            exit()

        print("Camera is found...")
        while cap.isOpened():
            if self.forceTerminate:
                break
            isCaptured, frame = cap.read()

            if isCaptured:
                self.__trackFrame__(frame, cameraMatrix, distCoeffs)

            # tracking fps = 30
            key = cv2.waitKey(math.floor(1000 / 30))
            if key == ord("q") or key == ord("Q"):
                break
        cap.release()
        cv2.destroyAllWindows()
        self.onTrackingFinish()

    # private
    def __trackFrame__(self, frame, cameraMatrix, distCoeffs):
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
                rotMat, _ = cv2.Rodrigues(rvecs[i])

                projMat = np.hstack((rotMat, tvecs[i]))
                eulerAngles = cv2.decomposeProjectionMatrix(projMat)[6]

                rollDegree, pitchDegree, yawDegrees = eulerAngles

                rollDegree = wrapAngle(rollDegree[0])
                pitchDegree = pitchDegree[0]
                yawDegrees = yawDegrees[0]

                rotation = np.array([rollDegree, pitchDegree, yawDegrees], np.float32)
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
                    filteredTvecs[i][0] = (
                        0.0 if self.app.varLockX.get() else filteredTvecs[i][0][0]
                    )
                    filteredTvecs[i][1] = (
                        0.0
                        if self.app.varLockY.get()
                        else filteredTvecs[i][1][0] * -1
                    )
                    filteredTvecs[i][2] = (
                        0.0 if self.app.varLockZ.get() else filteredTvecs[i][2][0]
                    )
                    filteredRotations[i][0] = (
                        0.0 if self.app.varLockRoll.get() else filteredRotations[i][0]
                    )
                    filteredRotations[i][1] = (
                        0.0
                        if self.app.varLockPitch.get()
                        else filteredRotations[i][1]
                    )
                    filteredRotations[i][2] = (
                        0.0 if self.app.varLockYaw.get() else filteredRotations[i][2]
                    )

            # send data
            self.client.sendCubeData(
                filteredMarkerIds, filteredTvecs, filteredRotations
            )

            self.onTrack(filteredMarkerIds, filteredTvecs, filteredRotations)
            isLastObjectGone = False

        else:
            if isLastObjectGone is False:
                self.client.sendCubeData([], [], [])
                self.onTrack([], [], [])
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
