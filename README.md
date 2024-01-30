# VReactable

VReactable is an interface connects the VR world and Reality. The tool runs on an VR platform named Resonite, which is a platform that users can customize their own space and writing scripts in the space. VReactable provides a tangible interface that users can manipulate a Resonite world by moving cubes in real world. This brings an oppotunity for users to interact with VR users in a different way.

![Overview](./assets/readme/overview_optimized.gif)

![VReactable](./assets/readme/vreactable-python_optimized.gif)

![Overview](./assets/readme/overview.PNG)

## Installation

You are not required to download the source code. To run this tool, you can simply download the [release version](https://github.com/willake/vreactable/releases/).

## Prerequisite

To use this tool, there are 3 components need to be prepared.

### Component 1: Webcam and Aruco Markers

#### Camera

Connect the webcam with your computer or laptop. Next, locate your camera above a plane like a empty table. The optimal height will be 80cm.

When camera is located, it is required to calibrate camera parameters. First, we need to print a Charuco Board. Charuco Board is a common material to calibrate the camera parameters for increasing accurancy of tracking. By clicking the button `Generate charuco board`, the board image will be generated in `${projectfolder}\resources\aruco\charuco_board`.

Now it is ready for calibration. Click the button `Capture sample images`, a window will show up. Then, present your Charuco Board in the camera view. When all the markers are tracked, press `S` on your keyboard to save the sample image. Take at least 20 images from different angles and distances can have a best quality of camera parameters.

![Sampling](./assets/readme/sampling_optimized.gif)

Lastly, press Calibrate camera to start calibration. In the end a `cali.npz` file should be seen at `${projectfolder}\resources\calibration`.

#### Aruco markers

Camera is ready, then you will need to have markers for tracking. Open `VReactable.exe`. There is a section called `Aruco Generator`. Usually users do not need to adjust any settings. By clicking button `Generate Aruco markers`, a set of Aruco markers will be generated in `${projectfolder}\resources\aruco\markers`. An easy printing version will be at `${projectfolder}\resources\aruco\packed`. For the markers, it will be more handy if they are attached to a cube.

![Markers](./assets/readme/markers.png)

-- placeholder for placing image --
The setup includes a camera and 36 aruco tags.

### Component 2: Websocket Server

To send data to Resonite, we will need a websocket server as a middleware. We use Chataigne as the websocket server since it is easy to setup. It is also possible to replace it by any other websocket server applications. The function of the server is to receive data from the tracking software and reflect(brodcast) the data to all clients.

To use Chataigne, first download the [1.9.7](https://benjamin.kuperberg.fr/chataigne/user/data/Chataigne-win-x64-1.9.7.exe) version. Next, download the [template](https://drive.google.com/file/d/11mTlseGczexTcRwXIAMDaV-fiIk-UgM_/view?usp=drive_link) we prepared. Load the template then websocket server is ready to go.

### Component 3: Resonite World

Next, download Resonite on Steam. Open Resonite and create a world. Import the VReactable inventory by copy `resrec:///G-HKU-Mixed-Reality/R-6586E3FF28427F32F9B8D2ADA8408D8DCEF6AE7894A49781AADAA08F7DB1FE57` and `Ctrl+V` in the game. Right click the object and save it to the inventory. Note that if it is not savable, it is because the current foloder is not a savable location.

![Visualizer-1](./assets/readme/visualizer-1_optimized.gif)
![Visualizer-2](./assets/readme/visualizer-2_optimized.gif)
![VReactable](./assets/readme/vreactable-tool_optimized.gif)

## Start Tracking

By clicking the `Detect` button on VReactable software, the tracking will start and send data to Resonite.

> Note that to increase the tracking quality, you can also adjust the camera settings like making it gray or lowering the exposure and increasing the gain. To do so, either use the driver of your webcam or OBS can help. Making the background dark is also very helpful.

![OBS Camera Settings](./assets/readme/obs.png)

![Tracking](./assets/readme/tracking_optimized.gif)
![Tracking Dark](./assets/readme/tracking_dark_optimized.gif)

## More questions?

If the question is regarding resonite, a possible solution is to visit [Resonite discord](https://discord.gg/resonite).

If it is a question about the code, you can contact me by emailing huienlin.game@gmail.com

## How to run from source code (Technical)

The environement I ran this code is Python `3.10.11`. If you are new to Python, I would recommend looking into pyenv for installing python. It provides a easier way to manage different versions of Python and also prevent corrupting the environment, which happens very often. (If you are using Windows, there is a [specific version for Windows](https://github.com/pyenv-win/pyenv-win).)

To install required packages, run

```
pip install -r requirements.txt
```

The code can be ran by typing

```
python vreactable.py
```

To build an executable file from the code. You can run `build.bat` (Windows only) or run

```
pyinstaller -F vreactable.py

# remember to copy config.ini and assets folder to the dist folder after building the software.

```

The file will appear in the `dist` folder.

## What need to improved (Technical)

- Run VReactable and OpenCV detector on different threads, so that you can force close OpenCV window when VReactable is closed.
