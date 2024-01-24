# VReactable

VReactable is an interface connects the VR world and Reality. The setup includes a camera and several aruco tags.

## Prepare markers

Open the VReactalbe program.

## Calibration

Calibration is a mandatory process for setting camera configurations for Aruco tracking. A well calibrated camera can produce more accurate tracking result.

### Generate and print a charuco board

To run calibration, firstly the user should generate an charuco board and print it out. Open the VReactable software, there is a `Generate charuco board` button for doing it.
The default pattern 5 x 7 is sufficient so normaly it is unncessary to change it.

### Capture sample images

When the board is prepared, press `Capture sample images` button. A camera view will show up. When the board is placed in the camera view, a gizmo of board paterrn appears. After then, sample images can be captured by pressing `S`. Captuing at least 20 sample images is recommended. The sample images should includes boards in different angles, distance.

### Calibrate camera

Lastly, press `Calibrate camera` to start calibration. In the end a `cali.npz` file in resources folder should be seen.

## Run Tracking

### Prepare resonite world

### Prepare websocket server

### Start tracking

Step 1: Setup Resonite
Step 2: Setup Cube
Step 2-1: Open VReactable software

Step 2-2: Prepare markers
Usually the user does not need to adjust any settings. By clicking button “Generate Aruco markers”, a set of Aruco markers will be generated in `${projectfolder}\resources\aruco\markers`. An easier printing version will be at `${projectfolder}\resources\aruco\packed’. 
Step 2-3: Prepare Charuco Board
Charuco Board is used for calibrating the camera parameters in order to accurately track cube states. By clicking the button `Generate charuco board`, the board image will be generated in `{projectfolder}\resources\aruco\charuco_board`. 
Step 2-4: Setup camera
Place your camera at 80 cm height from your table.
Step 2-5: Take sample images for calibration
Click the button `Capture sample images`. A window will show up, presenting your Charuco Board in camera view. When all the codes are tracked, press `S` on your keyboard to save the sampleimage. Take at least 20 images from different angles and distances to increase the quality of camera parameters.
Step 2-6: Calibrate

Step 3: Setup Chataigne Websocket Server
The detector uses a camera to detect cube positions and rotations. It produces the data and sends it to Resonite via websocket.
Step 4: Setup Detector

Step 2-2: Prepare markers
Usually the user does not need to adjust any settings. By clicking button “Generate Aruco markers”, a set of Aruco markers will be generated in `${projectfolder}\resources\aruco\markers`. An easier printing version will be at `${projectfolder}\resources\aruco\packed’. 
Step 2-3: Prepare Charuco Board
Charuco Board is used for calibrating the camera parameters in order to accurately track cube states. By clicking the button `Generate charuco board`, the board image will be generated in `{projectfolder}\resources\aruco\charuco_board`. 
Step 2-4: Setup camera
Place your camera at 80 cm height from your table.
Step 2-5: Take sample images for calibration
Click the button `Capture sample images`. A window will show up, presenting your Charuco Board in camera view. When all the codes are tracked, press `S` on your keyboard to save the sampleimage. Take at least 20 images from different angles and distances to increase the quality of camera parameters.
Step 2-6: Calibrate
Click the button

Step 3: Setup Chataigne Websocket Server
The detector uses a camera to detect cube positions and rotations. It produces the data and sends it to Resonite via websocket.
Step 4: Setup Detector
Step 4-1: Open the detector program

Calibration
Calibration is a mandatory process for setting camera configurations for Aruco tracking. A well calibrated camera can produce more accurate tracking result.

Generate and print a charuco board
To run calibration, firstly the user should generate an charuco board and print it out. Open the VReactable software, there is a Generate charuco board button for doing it. The default pattern 5 x 7 is sufficient so normaly it is unncessary to change it.

Capture sample images
When the board is prepared, press Capture sample images button. A camera view will show up. When the board is placed in the camera view, a gizmo of board paterrn appears. After then, sample images can be captured by pressing S. Captuing at least 20 sample images is recommended. The sample images should includes boards in different angles, distance.

Calibrate camera
Lastly, press Calibrate camera to start calibration. In the end a cali.npz file in resources folder should be seen.

Run Tracking
