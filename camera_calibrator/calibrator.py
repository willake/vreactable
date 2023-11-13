import cv2
from cv2 import aruco
import glob
import os
import numpy as np
import pathlib

# ChAruco board configs
PATTERN = (5, 7)
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)

CHARUCO_BOARD = aruco.CharucoBoard(
    size=PATTERN, 
    squareLength=0.04, 
    markerLength=0.02, 
    dictionary=ARUCO_DICT)

corners_all = []
ids_all = []
image_size = None # Determined at runtime

def validatePath(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

def calibrate():
    images = glob.glob(f'{pathlib.Path().resolve()}/inputs/samples/*.jpg')
    parameters = aruco.DetectorParameters()
    detector = aruco.CharucoDetector(board=CHARUCO_BOARD, parameters=parameters)
    
    # Loop through images glob
    for iname in images:
        img = cv2.imread(iname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        charucoCorners, charucoIds, markerCorners, markerIds = detector.detectBoard(gray)

        img = aruco.drawDetectedCornersCharuco(img, charucoCorners, charucoIds)
        corners_all.append(charucoCorners)
        ids_all.append(charucoIds)

        cv2.waitKey(0)
    
    if not image_size:
        image_size = gray.shape[::-1]

    calibration, cameraMatrix, distCoeffs, rvecs, tvecs = aruco.calibrateCameraCharuco(
        charucoCorners=corners_all,
        charucoIds=ids_all,
        board=CHARUCO_BOARD,
        imageSize=image_size)
    
    print(cameraMatrix)
    print(distCoeffs)
    
    directory = f'{pathlib.Path().resolve()}/outputs'
    np.savetxt(f'{directory}/camera_prams', mtx = cameraMatrix, distCoeffs = distCoeffs, delimiter=',', fmt='%.4f')
    
    # fileName = "inputs/images"
    # cap = cv2.VideoCapture(fileName)
    
    # while cap.isOpened():
    #     if cv2.waitKey(1) == 27:
    #         break


if __name__ == "__main__":
    calibrate()