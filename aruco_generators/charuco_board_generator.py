import cv2
from cv2 import aruco
import os 
import pathlib

PATTERN = (5, 7)
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

CHARUCO_BOARD = aruco.CharucoBoard(
    size=PATTERN, 
    squareLength=SQUARE_LENGTH, 
    markerLength=MARKER_LENGTH, 
    dictionary=ARUCO_DICT)
CHARUCO_BOARD.setLegacyPattern(True)

def validatePath(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

if __name__ == "__main__":

    markerImage = None

    directory = f"{pathlib.Path().resolve()}/outputs"
    validatePath(directory)
    boardImage = None
    boardImage = CHARUCO_BOARD.generateImage((595, 842), boardImage, 20, 1)
    cv2.imwrite(f"{directory}/charuco_board.png", boardImage)

    print(f"Generated the charuco board image")
    