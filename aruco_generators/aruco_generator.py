import cv2
from cv2 import aruco
import os
from helper import helper
        
def generateArucoMarkers(outputFolder, arucoDict, numOfImgs, size):
    # directory = f"{pathlib.Path().resolve()}/outputs/arucos"
    # validatePath(directory)

    for x in range(numOfImgs):
        markerImage = cv2.aruco.generateImageMarker(arucoDict, x, size)
        print(markerImage)
        cv2.imwrite(os.path.join(outputFolder, f"aruco_marker_{x}.png"), markerImage)

    print(f"Generated {numOfImgs} aruco images")

if __name__ == "__main__":
    generateArucoMarkers(
        outputFolder = f"{helper.getRootPath()}/outputs/arucos",
        arucoDict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50),
        numOfImgs = 50,
        size = 200
    )
    print(f"Generated {numOfImgs} aruco images")
    