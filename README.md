# VReactable

VReactable is an interface connects the VR world and Reality. The setup includes a camera and several aruco tags.

## Prepare markers

Open the VReactalbe program,

## Calibration

Calibration is a mandatory process for setting camera configurations for Aruco tracking. A well calibrated camera can produce more accurate tracking result.

### Generate and print a charuco board

To run calibration, firstly the user should generate an charuco board and print it out. Open the VReactable software, there is a `Generate charuco board` button for doing it.
The default pattern 5 x 7 is sufficient so normaly it is unncessary to change it.

### Capture sample images

When the board is prepared, press `Capture sample images` button. A camera view will show up. When the board is placed in the camera view, a gizmo of board paterrn appears. After then, sample images can be captured by pressing `S`. Captuing at least 20 sample images is recommended. The sample images should includes boards in different angles, distance.

### Calibrate camera

Lastly, press `Calibrate camera` to start calibration. In the end a `cali.npz` file in resources folder should be seen.

## Run

Camera
