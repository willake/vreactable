import cv2
import os 
import pathlib

def validatePath(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

if __name__ == "__main__":

    markerImage = None
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
    board = cv2.aruco.CharucoBoard((5, 7), 0.04, 0.02, dictionary)

    directory = f"{pathlib.Path().resolve()}/outputs/charuco_board"
    validatePath(directory)
    boardImage = None
    boardImage = board.generateImage((600, 500), boardImage, 10, 1)
    cv2.imwrite(f"{directory}/charuco_board.png", boardImage)

    print(f"Generated the charuco board image")
    