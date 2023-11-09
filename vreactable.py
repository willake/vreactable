import cv2

if __name__ == "__main__":
    markerImage = None
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
    markerImage = cv2.aruco.generateImageMarker(dictionary, 23, 200, markerImage, 1)
    print(markerImage)
    cv2.imshow("Image", markerImage)

    while True:
        if cv2.waitKey(1) == 27:
            break
        