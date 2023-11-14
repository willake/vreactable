import numpy as np
import cv2
from cv2 import aruco
import copy
import os
import pathlib

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

# objp = np.zeros((pattern[1] * pattern[0], 3), np.float32)
# objp[:, :2] = np.mgrid[0 : pattern[0], 0 : pattern[1]].T.reshape(-1, 2)

def detect(imageCopy, cameraMatrix, distCoeffs):
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
        
        rvecs = [None] * markerCount
        tvecs = [None] * markerCount

        for i in range(markerCount):
            retval, rvecs[i], tvecs[i] = cv2.solvePnP(OBJ_POINTS, markerCorners[i], cameraMatrix, distCoeffs)
        for i in range(markerCount):
            cv2.drawFrameAxes(imageCopy, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], 0.5)
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
    
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("error: cannot open camera")
        exit()
    while cap.isOpened():
        isCaptured, frame = cap.read()
        if isCaptured:
            imageCopy = copy.copy(frame)
            detect(imageCopy, cameraMatrix, distCoeffs)
            
        key = cv2.waitKey(33)
        if key == ord("q"):
            break
    

if __name__ == "__main__":
    path = f'{pathlib.Path().resolve()}/inputs/calib.npz'
    with np.load(path) as X:
        cameraMatrix, distCoeffs = [X[i] for i in ("cameraMatrix", "distCoeffs")]

    # print(cameraMatrix)
    # print(distCoeffs)
    run(cameraMatrix, distCoeffs)