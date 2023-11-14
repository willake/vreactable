import cv2
from cv2 import aruco
import glob
import os
import numpy as np
import pathlib

# ChAruco board configs
PATTERN = (5, 7)
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

CHARUCO_BOARD = aruco.CharucoBoard(
    size=PATTERN, 
    squareLength=SQUARE_LENGTH, 
    markerLength=MARKER_LENGTH, 
    dictionary=ARUCO_DICT)

# Generate Charuco board corners in 3D
OBJ_POINTS = CHARUCO_BOARD.getChessboardCorners()
# OBJ_POINTS = OBJ_POINTS.reshape(-1, 1, 3)

corners_all = []
ids_all = []
# image_size = None # Determined at runtime

def validatePath(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

def calibrate():
    images = glob.glob(f'{pathlib.Path().resolve()}/inputs/samples/*.jpg')
    detectorParams = aruco.DetectorParameters()
    detector = aruco.CharucoDetector(board=CHARUCO_BOARD, detectorParams=detectorParams)
    
    # Loop through images glob
    for iname in images:
        img = cv2.imread(iname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        charucoCorners, charucoIds, markerCorners, markerIds = detector.detectBoard(gray)

        img = aruco.drawDetectedCornersCharuco(img, charucoCorners, charucoIds)
        corners_all.append(charucoCorners)
        ids_all.append(charucoIds)
        
        cv2.imshow('calibrator', img)

        cv2.waitKey(0)
    
    image_size = None
    
    if image_size is None:
        image_size = gray.shape[::-1]

    calibration, cameraMatrix, distCoeffs, rvecs, tvecs = aruco.calibrateCameraCharuco(
        charucoCorners=corners_all,
        charucoIds=ids_all,
        board=CHARUCO_BOARD,
        imageSize=image_size,
        cameraMatrix=None,
        distCoeffs=None)
    
    # cv2.solvePnP(OBJ_POINTS, )
    
    print(cameraMatrix)
    print(distCoeffs)
    
    directory = f'{pathlib.Path().resolve()}/outputs'
    validatePath(directory)
    np.savez(f'{directory}/calib', cameraMatrix = cameraMatrix, distCoeffs = distCoeffs)
    
    # fileName = "inputs/images"
    # cap = cv2.VideoCapture(fileName)
    
    # while cap.isOpened():
    #     if cv2.waitKey(1) == 27:
    #         break


if __name__ == "__main__":
    calibrate()