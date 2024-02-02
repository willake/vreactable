import cv2
from cv2 import aruco
from PIL import Image, ImageDraw, ImageFont
from aruco_generators import aruco_generator
from aruco_generators import charuco_board_generator
from helper import helper

# import aruco_generator
import os

# Specify grid parameters
GRID_COLOR = (0, 0, 0)  # RGB color for grid lines (red in this case)
GRID_BORDER_WIDTH = 3  # Width of grid lines
FONT = ImageFont.load_default().font_variant(size=48)
TEXT_ALIGN = "center"

class MarkerGenerator:
    def __init__(self, onFail):
        self.onFail = onFail
        pass
    
    def generatePackedArucoMarkers(
    self,
    markerFolder, packedFolder, arucoDict, numMarkers, markerSizecm, gapSizecm, paperWidthcm, paperHeightcm
    ):
        arucoSize = markerSizecm + gapSizecm * 2
        if arucoSize > paperWidthcm or arucoSize > paperHeightcm:
            self.onFail("Marker size plus gap size is bigger than paper size.")
            return
        # Specify the folder to save ArUco markers and the number of markers to generate
        helper.clearFolder(markerFolder)
        helper.validatePath(markerFolder)

        aruco_generator.generateArucoMarkers(
            markerFolder,
            arucoDict,
            numMarkers,
            helper.cmToPixels(markerSizecm - gapSizecm * 2),
        )

        # Specify the folder containing ArUco markers, the output folder, and A4 size in centimeters
        helper.clearFolder(packedFolder)
        helper.validatePath(packedFolder)

        self.__packImages__(markerFolder, packedFolder, paperWidthcm, paperHeightcm, gapSizecm)
        pass


    def generateCharucoBoard(self, outputFolder, arucoDict, pattern, markerSizecm, gapSizecm):
        charuco_board_generator.generateCharucoboardImage(
            outputFolder=outputFolder,
            arucoDict=arucoDict,
            pattern=pattern,
            squareSizecm=markerSizecm + gapSizecm * 2,
            markerSizecm=markerSizecm,
        )
        pass
    

    def __packImages__(
        self,
        imagesFolder,
        outputFolder,
        paperWidthcm=21.0,
        paperHeightcm=29.7,
        gapSizecm=1.0,
        shouldDrawID=True,
    ):
        # Convert A4 size from centimeters to pixels
        paperWidth = helper.cmToPixels(paperWidthcm)
        paperHeight = helper.cmToPixels(paperHeightcm)
        gapSize = helper.cmToPixels(gapSizecm)

        # Get a list of ArUco marker image files in the specified folder
        arucoFiles = [
            f
            for f in os.listdir(imagesFolder)
            if f.startswith("aruco_marker") and f.endswith(".png")
        ]

        # Coordinates for placing ArUco markers on the A4 sheet
        x, y = gapSize, gapSize

        # Counter to keep track of the current image being processed
        imageCounter = 1

        # Create the first A4-sized image
        currentImage = Image.new("RGB", (paperWidth, paperHeight), "white")
        draw = ImageDraw.Draw(currentImage)

        arucoCount = 0

        draw.line([(0, 0), (paperWidth, 0)], fill=GRID_COLOR, width=GRID_BORDER_WIDTH)
        draw.line([(0, 0), (0, paperHeight)], fill=GRID_COLOR, width=GRID_BORDER_WIDTH)

        for arucoFile in arucoFiles:
            # Open each ArUco marker image
            arucoImg = Image.open(os.path.join(imagesFolder, arucoFile))

            # Resize the ArUco marker image to fit within the A4 sheet
            arucoImg.thumbnail((paperWidth, paperHeight))

            # Create a new A4-sized image if the current image is filled
            if x + arucoImg.size[1] + gapSize > paperWidth:
                # Save the current image
                outputPath = os.path.join(
                    outputFolder, f"packed_aruco_markers_{imageCounter}.jpg"
                )

                currentImage.save(outputPath)

                # Create a new A4-sized image
                currentImage = Image.new("RGB", (paperWidth, paperHeight), "white")
                draw = ImageDraw.Draw(currentImage)

                draw.line([(0, 0), (paperWidth, 0)], fill=GRID_COLOR, width=GRID_BORDER_WIDTH)
                draw.line([(0, 0), (0, paperHeight)], fill=GRID_COLOR, width=GRID_BORDER_WIDTH)

                # Reset coordinates for the new image
                x, y = gapSize, gapSize

                # Increment the image counter
                imageCounter += 1

            # Paste the ArUco marker image onto the current A4 sheet
            currentImage.paste(arucoImg, (x, y))

            if shouldDrawID:
                left, top, right, bottom = FONT.getbbox(str(arucoCount))
                tw = right - left
                th = bottom - top
                draw.text(
                    xy=(x + arucoImg.size[0] / 2 - tw / 2, y - gapSize),
                    text=str(arucoCount),
                    fill=GRID_COLOR,
                    font=FONT,
                    align=TEXT_ALIGN,
                )

            # Update the y-coordinate for the next ArUco marker
            y += arucoImg.size[1] + gapSize * 2
            draw.line(
                [(0, y - gapSize), (paperWidth, y - gapSize)],
                fill=GRID_COLOR,
                width=GRID_BORDER_WIDTH,
            )

            # If the ArUco marker image goes beyond the bottom of the A4 sheet, start a new column
            if y + arucoImg.size[1] + gapSize * 2 > paperHeight:
                x += arucoImg.size[0] + gapSize * 2
                y = gapSize
                draw.line(
                    [(x - gapSize, 0), (x - gapSize, paperHeight)],
                    fill=GRID_COLOR,
                    width=GRID_BORDER_WIDTH,
                )
                draw.line(
                    [
                        (x + arucoImg.size[1] + gapSize, 0),
                        (x + arucoImg.size[1] + gapSize, paperHeight),
                    ],
                    fill=GRID_COLOR,
                    width=GRID_BORDER_WIDTH,
                )

            arucoCount += 1

            # Save the last image if it contains content
            if currentImage:
                outputPath = os.path.join(
                    outputFolder, f"packed_aruco_markers_{imageCounter}.jpg"
                )
                currentImage.save(outputPath)