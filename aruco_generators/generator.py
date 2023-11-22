import cv2
from cv2 import aruco
from PIL import Image, ImageDraw
from aruco_generators import aruco_generator
from helper import helper 
# import aruco_generator
import os

def cmToPixels(cm, dpi=300):
    # 1 inch = 2.54 cm
    return int(cm * dpi / 2.54)

def packImages(imagesFolder, outputFolder, a4Widthcm=21.0, a4Heightcm=29.7, gapSizecm = 1.0):
    # Convert A4 size from centimeters to pixels
    a4Width = cmToPixels(a4Widthcm)
    a4Height = cmToPixels(a4Heightcm)
    gapSize = cmToPixels(gapSizecm)

    # Get a list of ArUco marker image files in the specified folder
    arucoFiles = [f for f in os.listdir(imagesFolder) if f.startswith('aruco_marker') and f.endswith('.png')]

    # Coordinates for placing ArUco markers on the A4 sheet
    x, y = gapSize, gapSize

    # Counter to keep track of the current image being processed
    image_counter = 1

    # Create the first A4-sized image
    currentImage = Image.new('RGB', (a4Width, a4Height), 'white')
    draw = ImageDraw.Draw(currentImage)

    for arucoFile in arucoFiles:
        # Open each ArUco marker image
        arucoImg = Image.open(os.path.join(imagesFolder, arucoFile))

        # Resize the ArUco marker image to fit within the A4 sheet
        arucoImg.thumbnail((a4Width, a4Height))

        # Create a new A4-sized image if the current image is filled
        if x + arucoImg.size[1] + gapSize > a4Width:
            # Save the current image
            output_path = os.path.join(outputFolder, f"packed_aruco_markers_{image_counter}.jpg")
            currentImage.save(output_path)

            # Create a new A4-sized image
            currentImage = Image.new('RGB', (a4Width, a4Height), 'white')
            draw = ImageDraw.Draw(currentImage)

            # Reset coordinates for the new image
            x, y = gapSize, gapSize

            # Increment the image counter
            image_counter += 1

        # Paste the ArUco marker image onto the current A4 sheet
        currentImage.paste(arucoImg, (x, y))

        # Update the y-coordinate for the next ArUco marker
        y += arucoImg.size[1] + gapSize * 2

        # If the ArUco marker image goes beyond the bottom of the A4 sheet, start a new column
        if y + arucoImg.size[1] > a4Height:
            x += arucoImg.size[0] + gapSize * 2
            y = gapSize

    # Save the last image if it contains content
    if currentImage:
        output_path = os.path.join(outputFolder, f"packed_aruco_markers_{image_counter}.jpg")
        currentImage.save(output_path)
        
def generatePackedArucoMarkers(arucoDict, numMarkers, markerSizecm, gapSizecm):
    # Specify the folder to save ArUco markers and the number of markers to generate
    arucoOutputFolder = "resources/aruco/markers"
    
    helper.clearFolder(arucoOutputFolder)
    helper.validatePath(arucoOutputFolder)

    aruco_generator.generateArucoMarkers(arucoOutputFolder, arucoDict, numMarkers, cmToPixels(markerSizecm))

    # Specify the folder containing ArUco markers, the output folder, and A4 size in centimeters
    imagesFolder = "resources/aruco/markers"
    outputFolder = "resources/aruco/packed"
    helper.clearFolder(outputFolder)
    helper.validatePath(imagesFolder)
    helper.validatePath(outputFolder)
    a4Widthcm = 21.0  # A4 width in centimeters
    a4Heightcm = 29.7  # A4 height in centimeters

    packImages(imagesFolder, outputFolder, a4Widthcm, a4Heightcm, gapSizecm)

if __name__ == "__main__":
    arucoDict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
    generatePackedArucoMarkers(arucoDict = arucoDict, numMarkers = 36, markerSizecm = 4.5, gapSizecm = 0.5)