import cv2
from cv2 import aruco
from helper import helper 
import os

SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

def cmToPixels(cm, dpi=300):
    # 1 inch = 2.54 cm
    return int(cm * dpi / 2.54)

def generateCharucoboardImage(outputFolder, arucoDict, pattern, squareSizecm, markerSizecm):
    helper.clearFolder(outputFolder)
    helper.validatePath(outputFolder)
    
    squareSize = cmToPixels(squareSizecm)
    markerSize = cmToPixels(markerSizecm)
    
    margin = 20
    
    charucoBoard = aruco.CharucoBoard(
        size=pattern, 
        squareLength=squareSize, 
        markerLength=markerSize, 
        dictionary=arucoDict)
    charucoBoard.setLegacyPattern(True)
    boardImage = None
    
    print(squareSize)
    
    row, column = pattern
    
    boardSize = (
        margin * 2 + row * squareSize,
        margin * 2 + column * squareSize 
    )
    
    ## calculate size
    boardImage = charucoBoard.generateImage(boardSize, boardImage, margin, 1)
    cv2.imwrite(f"{outputFolder}/charuco_board.png", boardImage)

    print(f"Generated the charuco board image")

if __name__ == "__main__":
    outputFolder = os.path.join(helper.getRootPath(), 'resources\\aruco\\charuco_board')
    generateCharucoboardImage(
        outputFolder = outputFolder,
        arucoDict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50),
        pattern = (5,7))

    print(f"Generated the charuco board image")
    