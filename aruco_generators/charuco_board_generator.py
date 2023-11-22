import cv2
from cv2 import aruco
from helper import helper 

SQUARE_LENGTH = 100
MARKER_LENGTH = 0.85 * 100

def generateCharucoboardImage(arucoDict, pattern):
    directory = f"{helper.getRootPath()}/resources/charuco_board"
    helper.clearFolder(directory)
    helper.validatePath(directory)
    
    charucoBoard = aruco.CharucoBoard(
        size=pattern, 
        squareLength=SQUARE_LENGTH, 
        markerLength=MARKER_LENGTH, 
        dictionary=arucoDict)
    charucoBoard.setLegacyPattern(True)
    boardImage = None
    boardImage = charucoBoard.generateImage((595, 842), boardImage, 20, 1)
    cv2.imwrite(f"{directory}/charuco_board.png", boardImage)

    print(f"Generated the charuco board image")

if __name__ == "__main__":
    generateCharucoboardImage(
        arucoDict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50),
        pattern = (5,7))

    print(f"Generated the charuco board image")
    