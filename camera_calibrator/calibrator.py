import cv2
from cv2 import aruco
import glob
import os
import numpy as np
from helper import helper
import camera_calibrator.sample_image_capturer as sample_image_capturer

SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

corners_all = []
ids_all = []
# image_size = None # Determined at runtime


class Calibrator:
    def __init__(self, sampleFolder, calibFolder, arucoDict, pattern, onFinish, onFail):
        self.sampleFolder = sampleFolder
        self.calibFolder = calibFolder
        self.arucoDict = arucoDict
        self.pattern = pattern
        self.onFinish = onFinish
        self.onFail = onFail
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
        accepted = False
        imageIdx = 1
        imageTotal = len(images)
        # Loop through images glob
        for iname in images:
            
            while True:
                img = cv2.imread(iname)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                charucoCorners, charucoIds, markerCorners, markerIds = detector.detectBoard(
                    gray
                )

                img = aruco.drawDetectedCornersCharuco(img, charucoCorners, charucoIds)
                    
                cv2.putText(
                    img,
                    f"Calibration           Now viewing image {imageIdx}/{imageTotal}",
                    (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 0),
                    1,
                )
                cv2.putText(
                    img,
                    f"This is the step for you to validate samples",
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 0),
                    1,
                )
                cv2.putText(
                    img,
                    f"Press A to accept sample",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 0, 255),
                    1,
                )
                cv2.putText(
                    img,
                    f"Press R to reject sample",
                    (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 0, 255),
                    1,
                )
                
                if len(corners_all) > 0:
                    if accepted:
                        cv2.putText(
                            img,
                            f"Previous sample is accepted",
                            (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            (0, 255, 0),
                            1,
                        )
                    else:
                        cv2.putText(
                            img,
                            f"Previous sample is rejected",
                            (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            (0, 0, 255),
                            1,
                        )
                        
                cv2.imshow("calibrator", img)

                key = cv2.waitKey(0)
                
                if key == ord("a") or key == ord("A"):
                    # save screenshot
                    if len(charucoIds) > 0:
                        corners_all.append(charucoCorners)
                        ids_all.append(charucoIds)
                    accepted = True
                    break
                elif key == ord("r") or key == ord("R"):
                    accepted = False
                    break
            imageIdx += 1
            
        cv2.destroyAllWindows()
        
        if len(corners_all) == 0:
            self.onFail("No sample images found")
            return

        try:
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
            
            print("=== Camera Matrix ===")
            print(cameraMatrix)
            print("=== Dist Coeffs ===")
            print(distCoeffs)
            print("=========")

            helper.validatePath(self.calibFolder)
            np.savez(
                os.path.join(self.calibFolder, "calib"),
                cameraMatrix=cameraMatrix,
                distCoeffs=distCoeffs,
            )
            
            print(f"calibration is done. The file is saved at {self.calibFolder}")
        
            self.onFinish()
        except Exception as e:
            self.onFail("Complex error. View the console to see more.")
            # raise e
        
