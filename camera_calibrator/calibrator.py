import cv2
from cv2 import aruco
import glob
import os
import numpy as np
import pathlib
from helper import helper

SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

corners_all = []
ids_all = []
# image_size = None # Determined at runtime


def calibrate(sampleFolder, calibFolder, arucoDict, pattern):
    images = glob.glob(f"{sampleFolder}\\*.jpg")
    detectorParams = aruco.DetectorParameters()
    charucoBoard = aruco.CharucoBoard(
        size=pattern,
        squareLength=SQUARE_LENGTH,
        markerLength=MARKER_LENGTH,
        dictionary=arucoDict,
    )
    objPoints = charucoBoard.getChessboardCorners()

    detector = aruco.CharucoDetector(board=charucoBoard, detectorParams=detectorParams)
    # Loop through images glob
    for iname in images:
        img = cv2.imread(iname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        charucoCorners, charucoIds, markerCorners, markerIds = detector.detectBoard(
            gray
        )

        img = aruco.drawDetectedCornersCharuco(img, charucoCorners, charucoIds)
        corners_all.append(charucoCorners)
        ids_all.append(charucoIds)

        cv2.imshow("calibrator", img)

        cv2.waitKey(0)

    image_size = None

    if image_size is None:
        image_size = gray.shape[::-1]

    calibration, cameraMatrix, distCoeffs, rvecs, tvecs = aruco.calibrateCameraCharuco(
        charucoCorners=corners_all,
        charucoIds=ids_all,
        board=charucoBoard,
        imageSize=image_size,
        cameraMatrix=None,
        distCoeffs=None,
    )

    print(cameraMatrix)
    print(distCoeffs)

    helper.validatePath(calibFolder)
    np.savez(
        os.path.join(calibFolder, "calib"),
        cameraMatrix=cameraMatrix,
        distCoeffs=distCoeffs,
    )


if __name__ == "__main__":
    calibrate(
        sampleFolder=f"{helper.getRootPath()}\\resources\\calibration\\samples",
        calibFolder=f"{helper.getRootPath()}\\resources\\clibration",
        arucoDict=aruco.getPredefinedDictionary(aruco.DICT_6X6_50),
        pattern=(5, 7),
    )
