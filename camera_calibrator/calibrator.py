import cv2
from cv2 import aruco
import glob
import os
import numpy as np
import pathlib
from helper import helper
import camera_calibrator.sample_image_capturer as sample_image_capturer

SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

corners_all = []
ids_all = []
# image_size = None # Determined at runtime


class Calibrator:
    def __init__(self, sampleFolder, calibFolder, arucoDict, pattern, onFinish):
        self.sampleFolder = sampleFolder
        self.calibFolder = calibFolder
        self.arucoDict = arucoDict
        self.pattern = pattern
        self.onFinish = onFinish
        pass

    def startCalibration(self):
        sample_image_capturer.captureSampleImages(self.sampleFolder)
        self.__calibrate__()
        pass

    def __calibrate__(self):
        images = glob.glob(f"{self.sampleFolder}\\*.jpg")
        detectorParams = aruco.DetectorParameters()
        charucoBoard = aruco.CharucoBoard(
            size=self.pattern,
            squareLength=SQUARE_LENGTH,
            markerLength=MARKER_LENGTH,
            dictionary=self.arucoDict,
        )

        detector = aruco.CharucoDetector(
            board=charucoBoard, detectorParams=detectorParams
        )
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

        (
            calibration,
            cameraMatrix,
            distCoeffs,
            rvecs,
            tvecs,
        ) = aruco.calibrateCameraCharuco(
            charucoCorners=corners_all,
            charucoIds=ids_all,
            board=charucoBoard,
            imageSize=image_size,
            cameraMatrix=None,
            distCoeffs=None,
        )

        print(cameraMatrix)
        print(distCoeffs)

        helper.validatePath(self.calibFolder)
        np.savez(
            os.path.join(self.calibFolder, "calib"),
            cameraMatrix=cameraMatrix,
            distCoeffs=distCoeffs,
        )
