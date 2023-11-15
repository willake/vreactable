import numpy as np
import cv2
from cv2 import aruco
import copy
import os
import pathlib
import define_origin
import sender

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

def detect(frame, cameraMatrix, distCoeffs, origin_rvec, origin_tvec):
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

        for i in range(markerCount):
            retval, rvecs[i], tvecs[i] = cv2.solvePnP(OBJ_POINTS, markerCorners[i], cameraMatrix, distCoeffs)
            # Convert rotation vector to rotation matrix
            rot_mat, _ = cv2.Rodrigues(rvecs[i])

            # Extract pitch, yaw, and roll from the rotation matrix
            pitch = np.arcsin(-rot_mat[1, 2])
            yaw = np.arctan2(rot_mat[0, 2], rot_mat[2, 2])
            roll = np.arctan2(rot_mat[1, 0], rot_mat[1, 1])

            # Convert angles from radians to degrees if needed
            pitch_degrees = np.degrees(pitch)
            yaw_degrees = np.degrees(yaw)
            roll_degrees = np.degrees(roll)
            rotations[i] = np.array([pitch_degrees, yaw_degrees, roll_degrees], np.float32)
        for i in range(markerCount):
            cv2.drawFrameAxes(imageCopy, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], 0.5)
        
        sender.send_object_data(WEBSOCKET, markerIds, tvecs, rotations)
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
    

if __name__ == "__main__":
    global WEBSOCKET
    path = f'{pathlib.Path().resolve()}/inputs/calib.npz'
    with np.load(path) as X:
        cameraMatrix, distCoeffs = [X[i] for i in ("cameraMatrix", "distCoeffs")]

    WEBSOCKET = sender.setup_websocket_client()
    # print(cameraMatrix)
    # print(distCoeffs)
    run(cameraMatrix, distCoeffs)