import os
import pathlib


def getRootPath():
    return pathlib.Path().resolve()


def clearFolder(folderPath):
    if os.path.exists(folderPath) == False:
        return
    # Iterate over all files and subdirectories in the folder
    for item in os.listdir(folderPath):
        itemPath = os.path.join(folderPath, item)

        # Check if the item is a file and delete it
        if os.path.isfile(itemPath):
            os.remove(itemPath)
            print(f"Deleted file: {itemPath}")

        # Check if the item is a subdirectory and delete it recursively
        elif os.path.isdir(itemPath):
            clearFolder(itemPath)
            os.rmdir(itemPath)
            print(f"Deleted directory: {itemPath}")


def validatePath(path):
    if os.path.exists(path) == False:
        os.makedirs(path)


def checkCalibFileExit(path):
    if os.path.exists(path):
        return True
    else:
        return False


def cmToPixels(cm, dpi=300):
    # 1 inch = 2.54 cm
    return int(cm * dpi / 2.54)


def countImages(folderPath):
    validatePath(folderPath)
    # List all files in the folder
    all_files = os.listdir(folderPath)

    # Filter out only image files (you can customize the list of extensions)
    # image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    imageExtensions = [".jpg"]
    imageFiles = [
        file
        for file in all_files
        if any(file.lower().endswith(ext) for ext in imageExtensions)
    ]

    # Count the number of image files
    numImages = len(imageFiles)

    return numImages
