# VReactable

VReactable is an interface connects the VR world and Reality. The tool runs on an VR platform named Resonite, which is a platform that users can customize their own space and writing scripts in the space. VReactable provides a tangible interface that users can manipulate a Resonite world by moving cubes in real world. This brings an oppotunity for users to interact with VR users in a different way. 

## Prerequisite
To use this tool, there are 3 components need to be prepared. 
### Component 1: Webcam and Aruco Markers
#### Camera
Connect the webcam with your computer or laptop. Next, locate your camera above a plane like a empty table. The optimal height will be 80cm. 

When camera is located, it is required to calibrate camera parameters. First, we need to print a Charuco Board. Charuco Board is a common material to calibrate the camera parameters for increasing accurancy of tracking. By clicking the button `Generate charuco board`, the board image will be generated in `${projectfolder}\resources\aruco\charuco_board`. 

Now it is ready for calibration. Click the button `Capture sample images`, a window will show up. Then, present your Charuco Board in the camera view. When all the markers are tracked, press `S` on your keyboard to save the sample image. Take at least 20 images from different angles and distances can have a best quality of camera parameters. 

Lastly, press Calibrate camera to start calibration. In the end a `cali.npz` file should be seen at `${projectfolder}\resources\calibration`.

#### Aruco markers
Camera is ready, then you will need to have markers for tracking. Open `VReactable.exe`. There is a section called `Aruco Generator`. Usually users do not need to adjust any settings. By clicking button `Generate Aruco markers`, a set of Aruco markers will be generated in `${projectfolder}\resources\aruco\markers`. An easy printing version will be at `${projectfolder}\resources\aruco\packed`. For the markers, it will be more handy if they are attached to a cube.

-- placeholder for placing image --
The setup includes a camera and 36 aruco tags.

### Component 2: Websocket Server
To send data to Resonite, we will need a websocket server as a middleware. We use Chataigne as the websocket server since it is easy to setup. It is also possible to replace it by any other websocket server applications. The function of the server is to receive data from the tracking software and reflect(brodcast) the data to all clients. 

To use Chataigne, first download the [1.9.7](https://benjamin.kuperberg.fr/chataigne/user/data/Chataigne-win-x64-1.9.7.exe) version. Next, download the [template](https://drive.google.com/file/d/11mTlseGczexTcRwXIAMDaV-fiIk-UgM_/view?usp=drive_link) we prepared. Load the template then websocket server is ready to go.

### Component 3: Resonite World
Next, download Resonite on Steam. Open Resonite and create a world. Import the VReactable inventory by copy `resrec:///G-HKU-Mixed-Reality/R-6586E3FF28427F32F9B8D2ADA8408D8DCEF6AE7894A49781AADAA08F7DB1FE57` and `Ctrl+V` in the game. Right click the object and save it to the inventory. Note that if it is not savable, it is because the current foloder is not a savable location.

### Start Tracking
By clicking the `Detect` button on VReactable software, the tracking will start and send data to Resonite.
