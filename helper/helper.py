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