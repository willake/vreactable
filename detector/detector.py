import numpy as np
import cv2
from cv2 import aruco
import copy
import os
import pathlib
from detector import sender
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
    dictionary=ARUCO_DICT)
OBJ_POINTS = np.zeros((4, 3), np.float32)
OBJ_POINTS[0] = np.array([[-MARKER_LENGTH /2., MARKER_LENGTH /2., 0]], np.float32)
OBJ_POINTS[1] = np.array([[MARKER_LENGTH /2., MARKER_LENGTH /2., 0]], np.float32)
OBJ_POINTS[2] = np.array([[MARKER_LENGTH /2., -MARKER_LENGTH /2., 0]], np.float32)
OBJ_POINTS[3] = np.array([[-MARKER_LENGTH /2.,-MARKER_LENGTH /2., 0]], np.float32)

origin_rvec = None

origin_tvec = None

isLastObjectGone = False

def wrapAngle(angle):
    """
    Wrap an angle to the range -180 to 180 degrees.

    Args:
        angle (float): Input angle in degrees.

    Returns:
        float: Wrapped angle in the range -180 to 180 degrees.
    """
    wrapped_angle = (angle + 180) % 360
    
    if wrapped_angle > 180: wrapped_angle = (wrapped_angle - 360)
    return wrapped_angle

def format(v):
    return "{:.2f}".format(round(v, 1))

def detect(frame, cameraMatrix, distCoeffs, origin_rvec, origin_tvec):
    global isLastObjectGone
    global WEBSOCKET
    imageCopy = copy.copy(frame)
    detectorParams = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary=ARUCO_DICT, detectorParams=detectorParams)
    
    markerCorners, markerIds, _ = detector.detectMarkers(imageCopy)
    
    isFound = (markerIds is not None) and len(markerIds) > 0
    
    if isFound:
        # print(OBJ_POINTS)
        # print(markerCorners[0])
        markerCount = len(markerIds)
        aruco.drawDetectedMarkers(imageCopy, markerCorners, markerIds)
        cv2.putText(
            imageCopy,
            f"Markers found",
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1)
        
        rotations = [None] * markerCount
        rvecs = [None] * markerCount
        tvecs = [None] * markerCount
        
        filteredMarkerIds = [-1] * 6
        filteredTvecs = [None] * 6
        filteredRvecs = [None] * 6
        filteredRotations = [np.array([360, 360, 360], np.float32)] * 6

        for i in range(markerCount):
            retval, rvecs[i], tvecs[i] = cv2.solvePnP(OBJ_POINTS, markerCorners[i], cameraMatrix, distCoeffs)
            # Convert rotation vector to rotation matrix
            rot_mat, _ = cv2.Rodrigues(rvecs[i])

            # # Extract pitch, yaw, and roll from the rotation matrix
            # pitch = np.arcsin(-rot_mat[1, 2])
            # yaw = np.arctan2(rot_mat[0, 2], rot_mat[2, 2])
            # roll = np.arctan2(rot_mat[1, 0], rot_mat[1, 1])
        
            proj_matrix = np.hstack((rot_mat, tvecs[i]))
            eulerAngles = cv2.decomposeProjectionMatrix(proj_matrix)[6] 
            
            roll_degrees, pitch_degrees, yaw_degrees = eulerAngles

            roll_degrees = wrapAngle(roll_degrees[0])
            tmp_pitch = -pitch_degrees[0]
            pitch_degrees =  yaw_degrees[0]
            yaw_degrees = tmp_pitch
            
            #print(f"{format(pitch_degrees)}, {format(yaw_degrees)}, {format(roll_degrees)}")
            
            # quaternion = GetQuaternionFromEuler(math.radians(roll_degrees), math.radians(pitch_degrees), math.radians(yaw_degrees))
            # pitch = pitch
            # roll = roll
            # yaw = yaw
            # # tmpYaw = roll
            # # roll = yaw
            # # yaw = tmpYaw
            
            # pitch_degrees = math.degrees(math.asin(math.sin(pitch)))
            # roll_degrees = -math.degrees(math.asin(math.sin(roll)))
            # yaw_degrees = math.degrees(math.asin(math.sin(yaw)))
            
            # roll = roll + (math.pi / 2)

            # Convert angles from radians to degrees if needed
            # pitch_degrees = np.degrees(pitch)
            # yaw_degrees = np.degrees(yaw)
            # roll_degrees = np.degrees(roll)
            rotation = np.array([roll_degrees, pitch_degrees, yaw_degrees], np.float32)
            # filter by rotations so there will be only 1 marker on a box being detected
            cubeIndex = int(markerIds[i] / 6)
            # pitch diff with platform
            rollDiff = abs(roll_degrees)
            yawDiff = abs(yaw_degrees)
            if rollDiff < abs(filteredRotations[cubeIndex][0]) and yawDiff < abs(filteredRotations[cubeIndex][2]):
                filteredMarkerIds[cubeIndex] = markerIds[i]
                filteredTvecs[cubeIndex] = tvecs[i]
                filteredRvecs[cubeIndex] = rvecs[i]
                filteredRotations[cubeIndex] = rotation
            
        for i in range(6):
            if filteredMarkerIds[i] != -1:
                cv2.drawFrameAxes(imageCopy, cameraMatrix, distCoeffs, filteredRvecs[i], filteredTvecs[i], 0.5)
        
        sender.send_object_data(WEBSOCKET, filteredMarkerIds, filteredTvecs, filteredRotations)
        isLastObjectGone = False
        # if markerCount > 1:
            # Convert rotation vector to rotation matrix
            # rot_mat, _ = cv2.Rodrigues(rvecs[0])

            # Extract pitch, yaw, and roll from the rotation matrix
            # pitch = np.arcsin(-rot_mat[1, 2])
            # yaw = np.arctan2(rot_mat[0, 2], rot_mat[2, 2])
            # roll = np.arctan2(rot_mat[1, 0], rot_mat[1, 1])

            # Convert angles from radians to degrees if needed
            # pitch_degrees = np.degrees(pitch)
            # yaw_degrees = np.degrees(yaw)
            # roll_degrees = np.degrees(roll)
        
            # print(f'pitch_degrees: {pitch_degrees} yaw_degrees: {yaw_degrees} roll_degrees: {roll_degrees}')
            # print(f'tvec_0: {np.array_str(tvecs[0], precision=3, suppress_small=True)} tvec_1: {np.array_str(tvecs[1], precision=3, suppress_small=True)}')
    else:
        if isLastObjectGone is False:
            sender.send_object_data(WEBSOCKET, [], [], [])
            isLastObjectGone = True
        cv2.putText( 
            imageCopy,
            f"Markers not found",
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1)
    
    cv2.putText(
            imageCopy,
            f"Press Q to leave",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1)
        
    cv2.imshow("detector", imageCopy)
    
    return markerCorners, markerIds
    
def run(cameraMatrix, distCoeffs):
    global origin_rvec, origin_tvec
    
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("error: cannot open camera")
        exit()
    
    print("Camera is found...")
    while cap.isOpened():
        isCaptured, frame = cap.read()
        
        # if (origin_rvec is None) and (origin_tvec is None):
        #     origin_rvec, origin_tvec = define_origin.define_origin(frame, cameraMatrix, distCoeffs)
        #     continue
        if isCaptured:
            detect(frame, cameraMatrix, distCoeffs, origin_rvec, origin_tvec)
            
        key = cv2.waitKey(33)
        if key == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
        
def detect_arucos(calibFilePath: str, ip: str):
    global WEBSOCKET
    with np.load(calibFilePath) as X:
        cameraMatrix, distCoeffs = [X[i] for i in ("cameraMatrix", "distCoeffs")]
    print("Calibration file is loaded...")
    WEBSOCKET = sender.setup_websocket_client(ip)
    print("Websocket is set...")
    run(cameraMatrix, distCoeffs)

if __name__ == "__main__":
    global WEBSOCKET
    path = f'{pathlib.Path().resolve()}/inputs/calib.npz'
    with np.load(path) as X:
        cameraMatrix, distCoeffs = [X[i] for i in ("cameraMatrix", "distCoeffs")]

    WEBSOCKET = sender.setup_websocket_client()
    # print(cameraMatrix)
    # print(distCoeffs)
    run(cameraMatrix, distCoeffs)