import numpy as np
import cv2
from cv2 import aruco
import copy
import os
import pathlib

# ChAruco board configs
PATTERN = (5, 7)
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)

CHARUCO_BOARD = aruco.CharucoBoard(
    size=PATTERN, 
    squareLength=0.04, 
    markerLength=0.02, 
    dictionary=ARUCO_DICT)

OBJ_POINTS = np.zeros((1, 3), np.float32)

# objp = np.zeros((pattern[1] * pattern[0], 3), np.float32)
# objp[:, :2] = np.mgrid[0 : pattern[0], 0 : pattern[1]].T.reshape(-1, 2)

def detect(imageCopy, cameraMatrix, distCoeffs):
    detectorParams = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary=ARUCO_DICT, detectorParams=detectorParams)
    
    markerCorners, markerIds, _ = detector.detectMarkers(imageCopy)
    
    isFound = (markerIds is not None) and len(markerIds) > 0
    
    if isFound:
        aruco.drawDetectedMarkers(imageCopy, markerCorners, markerIds)
        cv2.putText(
        imageCopy,
        f"Markers found",
        (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1)
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
    
    print('run')
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
    cameraMatrix, distCoeffs = np.load(path)
    run(cameraMatrix, distCoeffs)