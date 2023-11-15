import copy
import cv2
import numpy as np

# table corner object points
OBJ_POINTS = np.zeros((4, 3), np.float32)
OBJ_POINTS[0] = np.array([[0, 0, 0]], np.float32)
OBJ_POINTS[1] = np.array([[50, 0, 0]], np.float32)
OBJ_POINTS[2] = np.array([[0, -35, 0]], np.float32)
OBJ_POINTS[3] = np.array([[50, -35, 0]], np.float32)

def define_origin(image, cameraMatrix, distCoeffs):
    imageCopy = copy.copy(image)
    tableCorners = setChessboardCornersByClicking('Define Table Corners', imageCopy)
    
    retval, rvec, tvec = cv2.solvePnP(OBJ_POINTS, tableCorners, cameraMatrix, distCoeffs)
    
    return rvec, tvec

# handle mouse click for setting corners
def setCornerClick(event, x, y, flags, params):
    global mousePosX, mousePosY
    [windowName, imageCopy, corners] = params

    if len(corners) > 3:
        return
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONUP:
        print(f"corner {len(corners)}: [{x}, {y}]")
        # set corner and add it in to corners array
        corners.append(np.array([(x, y)], np.float32))

        # draw text to indicate location and index
        cv2.putText(
            imageCopy,
            f"Sampling: please click {getFourCornerText(len(corners))} corner of the table",
            (10, 40 + (len(corners) * 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1,
        )
        cv2.circle(imageCopy, (x, y), 2, (0, 0, 255), 2)
        cv2.putText(
            imageCopy,
            f"{len(corners)}:{(x, y)}",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )
        cv2.imshow(windowName, imageCopy)

# help instruction to get the text of corners
def getFourCornerText(idx):
    if idx == 0:
        return "top left"
    elif idx == 1:
        return "top right"
    elif idx == 2:
        return "bottom left"
    else:
        return "bottom right"
    
# start setting corners for chessboard
def setChessboardCornersByClicking(windowName, imageCopy):
    corners = []

    # show instructions
    cv2.putText(
        imageCopy,
        f"Defining Corners",
        (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        imageCopy,
        f"Sampling: please click {getFourCornerText(len(corners))} corner of the chessboard",
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )

    cv2.imshow(windowName, imageCopy)

    cv2.setMouseCallback(
        windowName, setCornerClick, [windowName, imageCopy, corners]
    )

    while len(corners) < 4:
        cv2.waitKey(33)
        
    cv2.setMouseCallback(windowName, lambda *args : None)

    return np.array(corners)