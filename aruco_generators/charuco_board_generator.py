import cv2
from cv2 import aruco
import os 
import pathlib

PATTERN = (5, 7)
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)

def validatePath(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

if __name__ == "__main__":

    markerImage = None
    board = aruco.CharucoBoard((5, 7), 0.04, 0.02, ARUCO_DICT)

    directory = f"{pathlib.Path().resolve()}/outputs"
    validatePath(directory)
    boardImage = None
    boardImage = board.generateImage((600, 500), boardImage, 10, 1)
    cv2.imwrite(f"{directory}/charuco_board.png", boardImage)

    print(f"Generated the charuco board image")
    