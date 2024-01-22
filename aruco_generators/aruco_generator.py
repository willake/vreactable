import cv2
from cv2 import aruco
import os
from helper import helper
        
def generateArucoMarkers(outputFolder, arucoDict, numOfImgs, size):
    for x in range(numOfImgs):
        markerImage = cv2.aruco.generateImageMarker(arucoDict, x, size)
        if x < 10 and x > 0:
            cv2.imwrite(os.path.join(outputFolder, f"aruco_marker_0{x}.png"), markerImage)
        else:
            cv2.imwrite(os.path.join(outputFolder, f"aruco_marker_{x}.png"), markerImage)
    print(f"Generated {numOfImgs} aruco images")

if __name__ == "__main__":
    generateArucoMarkers(
        outputFolder = f"{helper.getRootPath()}/outputs/arucos",
        arucoDict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50),
        numOfImgs = 50,
        size = 200
    )
    print(f"Generated {50} aruco images")
    