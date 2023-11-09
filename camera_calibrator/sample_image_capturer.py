import numpy as np
import cv2 as cv
import copy
import const
import path_getter as pg

# the purpose of this script is to capture
# detectable and undetectable images from the webcam
# users can run this script and capture good and bad images
# by pressing 'S'


# validate the detectable images
def validate(windowName, image, pattern, goodAmount, badAmount):
    # prepare object points
    objp = np.zeros((pattern[1] * pattern[0], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : pattern[0], 0 : pattern[1]].T.reshape(-1, 2)

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    cv.imshow(windowName, image)

    # find the chess board corners
    isFound, corners = cv.findChessboardCorners(
        gray,
        pattern,
        cv.CALIB_CB_ADAPTIVE_THRESH
        + cv.CALIB_CB_FAST_CHECK
        + cv.CALIB_CB_NORMALIZE_IMAGE,
    )

    # set instructions text for setting next image
    cv.putText(
        image,
        f"Capture images    Now captured {goodAmount} good images, and {badAmount} bad images",
        (10, 20),
        cv.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv.putText(
        image,
        f"Press S to take screenshot",
        (10, 40),
        cv.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )
    cv.putText(
        image,
        f"Press Q to exit",
        (10, 60),
        cv.FONT_HERSHEY_SIMPLEX,
        0.4,
        (255, 255, 255),
        1,
    )

    # if found, add object points, image points (after refining them)
    if isFound:
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), const.criteria)

        # draw corners
        cv.drawChessboardCorners(image, pattern, corners2, True)

        # set instructions text for setting next image
        cv.putText(
            image,
            f"corners are found",
            (10, 80),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            1,
        )
    else:
        # set instructions text for setting next image
        cv.putText(
            image,
            f"corners are not found",
            (10, 80),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            1,
        )

    cv.imshow(windowName, image)
    return isFound


# run camera
def run(pattern, outputFolder):
    goodAmount = 0
    badAmount = 0
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("error: cannot open camera")
        exit()
    while cap.isOpened():
        found, frame = cap.read()

        if not found:
            print("error: can't receive frame (stream end?). Exiting ...")
            break

        print("camera is captured, now showing the camera")

        frameCopy = copy.copy(frame)

        result = validate("camera", frameCopy, pattern, goodAmount, badAmount)

        key = cv.waitKey(33)
        if key == ord("s"):
            # save screenshot
            cv.imwrite(f"{outputFolder}/screenshot_{goodAmount + badAmount}.jpg", frame)
            if result:
                goodAmount += 1
            else:
                badAmount += 1
        elif key == ord("q"):
            break

    # release everything if job is finished
    cap.release()

    cv.destroyAllWindows()


if __name__ == "__main__":
    run((9, 6), pg.getSamepleScreenshotFolder())