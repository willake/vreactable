import cv2
from cv2 import aruco
import os 
import pathlib

ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)

def validatePath(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

if __name__ == "__main__":
    markerImage = None

    directory = f"{pathlib.Path().resolve()}/outputs/arucos"
    validatePath(directory)
    numOfImgs = 50

    for x in range(numOfImgs):
        markerImage = cv2.aruco.generateImageMarker(ARUCO_DICT, x, 200, markerImage, 1)
        print(markerImage)
        cv2.imwrite(f"{directory}/{x}.png", markerImage)

    print(f"Generated {numOfImgs} aruco images")
    