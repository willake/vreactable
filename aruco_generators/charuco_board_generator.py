import cv2
from cv2 import aruco
from helper import helper 
import os

SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

def generateCharucoboardImage(outputFolder, arucoDict, pattern):
    helper.clearFolder(outputFolder)
    helper.validatePath(outputFolder)
    
    charucoBoard = aruco.CharucoBoard(
        size=pattern, 
        squareLength=SQUARE_LENGTH, 
        markerLength=MARKER_LENGTH, 
        dictionary=arucoDict)
    charucoBoard.setLegacyPattern(True)
    boardImage = None
    boardImage = charucoBoard.generateImage((595, 842), boardImage, 20, 1)
    cv2.imwrite(f"{outputFolder}/charuco_board.png", boardImage)

    print(f"Generated the charuco board image")

if __name__ == "__main__":
    outputFolder = os.path.join(helper.getRootPath(), 'resources\\aruco\\charuco_board')
    generateCharucoboardImage(
        outputFolder = outputFolder,
        arucoDict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50),
        pattern = (5,7))

    print(f"Generated the charuco board image")
    