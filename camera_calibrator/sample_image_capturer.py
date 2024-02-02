import numpy as np
import cv2
from cv2 import aruco
import copy
import os
import pathlib
from helper import helper

# the purpose of this script is to capture
# detectable and undetectable images from the webcam
# users can run this script and capture good and bad images
# by pressing 'S'

# ChAruco board configs
PATTERN = (5, 7)
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

CHARUCO_BOARD = aruco.CharucoBoard(
    size=PATTERN,
    squareLength=SQUARE_LENGTH,
    markerLength=MARKER_LENGTH,
    dictionary=ARUCO_DICT,
)


# validate the detectable images
def detect(windowName, imageCopy, amount):
    # prepare object points
    detectorParams = aruco.DetectorParameters()
    detector = aruco.CharucoDetector(board=CHARUCO_BOARD, detectorParams=detectorParams)

    # Increase contrast using histogram equalization
    # lab = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2LAB)
    # l, a, b = cv2.split(lab)
    # clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    # l = clahe.apply(l)
    # lab = cv2.merge((l, a, b))
    # imageCopy = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    gray = cv2.cvtColor(imageCopy, cv2.COLOR_BGR2GRAY)

    cv2.imshow(windowName, imageCopy)

    # find the chess board corners
    charucoCorners, charucoIds, markerCorners, markerIds = detector.detectBoard(gray)

    isFound = (charucoIds is not None) and len(charucoIds) == (PATTERN[0] - 1) * (
        PATTERN[1] - 1
    )
    # set instructions text for setting next image
    cv2.putText(
        imageCopy,
        f"Capture images for calibration    Now captured {amount} images",
        (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (0, 255, 0),
        1,
    )
    cv2.putText(
        imageCopy,
        f"Press S to take sample when you see marker ids are detected",
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (0, 0, 255),
        1,
    )
    cv2.putText(
        imageCopy,
        f"It is normal if an image is not saved, because bad images are filtered automatically",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (0, 255, 0),
        1,
    )
    cv2.putText(
        imageCopy,
        f"Press Q to exit and start calibration",
        (10, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (0, 0, 255),
        1,
    )

    # if found, add object points, image points (after refining them)
    if isFound:
        imageCopy = aruco.drawDetectedCornersCharuco(
            imageCopy, charucoCorners, charucoIds
        )

        # set instructions text for setting next image
        cv2.putText(
            imageCopy,
            f"corners are found",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            1,
        )
    else:
        # set instructions text for setting next image
        cv2.putText(
            imageCopy,
            f"corners are not found",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            1,
        )

    cv2.imshow(windowName, imageCopy)
    return isFound


# run camera
def run(outputFolder):
    helper.clearFolder(outputFolder)
    imageAmount = 0
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("error: cannot open camera")
        exit()
    
    print("camera is captured, start sampling...")
    while cap.isOpened():
        found, frame = cap.read()

        if not found:
            print("error: can't receive frame (stream end?). Exiting ...")
            break

        frameCopy = copy.copy(frame)

        result = detect("camera", frameCopy, imageAmount)

        key = cv2.waitKey(33)
        if key == ord("s") or key == ord("S"):
            # save screenshot
            if result:
                cv2.imwrite(
                    f"{outputFolder}\\screenshot_{imageAmount}.jpg", frame
                )
                imageAmount += 1
        elif key == ord("q") or key == ord("Q"):
            break

    # release everything if job is finished
    cap.release()

    cv2.destroyAllWindows()


def captureSampleImages(sampleFolder):
    helper.validatePath(sampleFolder)
    run(sampleFolder)


if __name__ == "__main__":
    sampleFolder = os.path.join(helper.getRootPath(), "resources\\calibration\\samples")
    captureSampleImages(sampleFolder)
