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
        
def count_images(folder_path):
    # List all files in the folder
    all_files = os.listdir(folder_path)

    # Filter out only image files (you can customize the list of extensions)
    # image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    image_extensions = ['.jpg']
    image_files = [file for file in all_files if any(file.lower().endswith(ext) for ext in image_extensions)]

    # Count the number of image files
    num_images = len(image_files)

    return num_images