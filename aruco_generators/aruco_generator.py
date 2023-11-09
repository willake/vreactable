import cv2
import os 
import pathlib

def validatePath(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

if __name__ == "__main__":
    markerImage = None
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)

    directory = f"{pathlib.Path().resolve()}/outputs/arucos"
    validatePath(directory)
    numOfImgs = 50

    for x in range(numOfImgs):
        markerImage = cv2.aruco.generateImageMarker(dictionary, x, 200, markerImage, 1)
        print(markerImage)
        cv2.imwrite(f"{directory}/{x}.png", markerImage)

    print(f"Generated {numOfImgs} aruco images")

    # while True:
    #     if cv2.waitKey(1) == 27:
    #         break
    