import pathlib
from tkinter.messagebox import showerror, showwarning, showinfo
from camera_calibrator import sample_image_capturer, calibrator
import cv2.aruco as aruco
from camera_calibrator.calibrator import Calibrator
from tracker.tracker import CubeTracker
from aruco_generators import generator
from helper import helper, ui_helper
import pathlib
import os
import configparser
import sys
from threading import *

config = configparser.ConfigParser()
config.read("./config.ini")

from ttkbootstrap import Style
import tkinter as tk
from tkinter import ttk

MARKER_FOLDER = os.path.join(helper.getRootPath(), config["PATH"]["MarkerFolder"])
PACKED_FOLDER = os.path.join(helper.getRootPath(), config["PATH"]["PackedFolder"])
CHARUCO_FOLDER = os.path.join(helper.getRootPath(), config["PATH"]["CharucoFolder"])
SAMPLE_FOLDER = os.path.join(helper.getRootPath(), config["PATH"]["SampleFolder"])
CALIB_FOLDER = os.path.join(helper.getRootPath(), config["PATH"]["CalibFolder"])

ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
CHARUCO_BOARD_PATTERN = (5, 7)
VERSION = "v2.3"


class VreactableApp:
    def __init__(self, master=None):
        self.calibrator = Calibrator(
            SAMPLE_FOLDER,
            CALIB_FOLDER,
            ARUCO_DICT,
            CHARUCO_BOARD_PATTERN,
            self.onCalibrationFinish,
            self.onCalibrationFail
        )
        self.tracker = CubeTracker(self, self.onTrack, self.onTrackingFinish, self.onTrackingFail)
        self.trackingThread = None
        self.calibrationThread = None

        # start building GUI
        style = Style(theme="darkly")
        self.root = style.master
        self.root.title(f"VRectable {VERSION}")
        self.frameMain = ttk.Frame(self.root)
        self.frameMain.grid(row=0, column=0, padx=20, pady=10, sticky=tk.NSEW)

        # the image asset
        self.imgRefresh = tk.PhotoImage(file="assets/refresh.png")
        
        self.availableCameras = helper.getAvailableCameras()
        defaultCamName = ""
        
        if len(self.availableCameras) > 0:
            defaultCamName = self.availableCameras[0]
        
        self.varArucoSize = tk.StringVar(value="5")
        self.varArucoGapSize = tk.StringVar(value="0.5")
        self.varPrintPaperWidth = tk.StringVar(value="21.0")
        self.varPrintPaperHeight = tk.StringVar(value="29.7")
        self.varCameraIndex = tk.IntVar(value=0)
        self.varSelectedCamera = tk.StringVar(value=defaultCamName)
        # trace selected camera to set camera index
        self.varSelectedCamera.trace_add('write', self.onNewCameraSelected)
        self.varWebsocketIP = tk.StringVar(value="ws://localhost:8090")
        self.varLockX = tk.BooleanVar(value=False)
        self.varLockY = tk.BooleanVar(value=False)
        self.varLockZ = tk.BooleanVar(value=False)
        self.varLockRoll = tk.BooleanVar(value=False)
        self.varLockPitch = tk.BooleanVar(value=False)
        self.varLockYaw = tk.BooleanVar(value=False)

        # tk.StringVar(value="[0; 0; 0]") * 6 will not working, they will all point to same address
        self.varCubeActiveMarkerIDs = [
            tk.StringVar(value="-"),
            tk.StringVar(value="-"),
            tk.StringVar(value="-"),
            tk.StringVar(value="-"),
            tk.StringVar(value="-"),
            tk.StringVar(value="-"),
        ]
        self.varCubePositions = [
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
        ]
        self.varCubeRotations = [
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
            tk.StringVar(value="[0; 0; 0]"),
        ]
        
        # initialize button array for state control (enable/disable)
        self.interactables = []

        # title
        frameHeader = ttk.Frame(self.frameMain)
        labelTitle = ttk.Label(frameHeader, text=f"VReactable {VERSION}")
        labelTitle.grid(row=0, column=0, pady=5)
        frameHeader.grid(row=0, column=0, padx=10)
        self.varIsCalibrated = tk.StringVar(value="False")
        self.varIsCameraReady = tk.StringVar(value="False")

        # main frame
        frameBody = ttk.Frame(self.frameMain)

        # frame 1
        frame1 = ttk.Frame(frameBody)
        frameArucoGenerator = self.drawFrameArucoGenerator(frame1)
        frameCalibrator = self.drawFrameCalibrator(frame1)
        # organize layout
        frameArucoGenerator.grid(
            row=0, column=0, ipadx=15, ipady=5, pady=10, sticky=tk.EW
        )
        frameCalibrator.grid(row=1, column=0, ipadx=15, ipady=5, pady=1, sticky=tk.EW)
        frame1.grid(row=0, column=0, padx=10, sticky=tk.N)
        frame1.columnconfigure(0, weight=1)

        # frame 2
        frame2 = ttk.Frame(frameBody)
        frameTracker = self.drawFrameTracker(frame2)
        frameTracker.grid(row=0, column=0, ipadx=10, ipady=15, pady=10, sticky=tk.EW)
        frame2.grid(row=0, column=1, padx=10)
        frame2.columnconfigure(0, weight=1)

        # frame 3
        frame3 = ttk.Frame(frameBody)
        frameTrackingInspector = self.drawFrameTrackingInspector(frame3)
        frameTrackingInspector.grid(
            row=0, column=0, ipadx=10, ipady=15, pady=10, sticky=tk.EW
        )
        frame3.grid(row=0, column=2, padx=10)
        frame3.columnconfigure(0, weight=1)

        frameBody.grid(row=1, column=0, pady=5)
        frameBody.rowconfigure(0, weight=1)
        frameBody.columnconfigure(0, weight=2)
        frameBody.columnconfigure(1, weight=1)
        frameBody.columnconfigure(2, weight=2)

        # Main widget
        self.mainwindow = self.root
        self.mainwindow.protocol("WM_DELETE_WINDOW", self.onRootWindowClose)

        self.refreshStatus()

    def disableButtons(self):
        for interactable in self.interactables:
            interactable.configure(state=tk.DISABLED)
        pass

    def enableButtons(self):
        for interactable in self.interactables:
            interactable.configure(state=tk.NORMAL)
        pass

    def drawFrameArucoGenerator(self, parent):
        # aruco generator
        frame = ttk.Labelframe(parent, text="Aruco Generator")
        textFieldMarkerSize, entryMarkerSize = ui_helper.drawCMNumberField(
            frame, self.varArucoSize, "Marker size", "5"
        )
        textFieldGapSize, entryGapSize = ui_helper.drawCMNumberField(
            frame, self.varArucoGapSize, "Gap size", "0.5"
        )
        textFieldPrintPaperWidth, entryPrintPaperWidth = ui_helper.drawCMNumberField(
            frame, self.varPrintPaperWidth, "Print paper width", "21.0"
        )
        textFieldPrintPaperHeight, entryPrintPaperHeight = ui_helper.drawCMNumberField(
            frame, self.varPrintPaperHeight, "Print paper height", "29.7"
        )
        btnGenerate = ui_helper.drawButton(
            frame, "Generate aruco markers", self.onClickGenerateAruco
        )
        
        self.interactables.append(entryMarkerSize)
        self.interactables.append(entryGapSize)
        self.interactables.append(entryPrintPaperWidth)
        self.interactables.append(entryPrintPaperHeight)
        self.interactables.append(btnGenerate)

        textFieldMarkerSize.grid(row=0, column=0, pady=5)
        textFieldGapSize.grid(row=1, column=0, pady=5)
        textFieldPrintPaperWidth.grid(row=2, column=0, pady=5)
        textFieldPrintPaperHeight.grid(row=3, column=0, pady=5)
        btnGenerate.grid(row=4, column=0, ipadx=10, pady=5)

        frame.columnconfigure(0, weight=1)
        return frame

    def drawFrameCalibrator(self, parent):
        frame = ttk.Labelframe(parent, text="Camera Calibratior")

        btnGenerate = ui_helper.drawButton(
            frame, "Generate charuco board", self.onClickGenerateCharucoBoard
        )

        btnCalibrate = ui_helper.drawButton(
            frame, "Calibrate camera", self.onClickCalibrateCamera
        )
        
        self.interactables.append(btnGenerate)
        self.interactables.append(btnCalibrate)

        btnGenerate.grid(row=0, column=0, pady=5)
        btnCalibrate.grid(row=1, column=0, pady=5)
        frame.columnconfigure(index=0, weight=1)

        return frame

    def drawFrameCalibratorStatus(self, parent):
        frame = ttk.Labelframe(parent, text="Status")

        stateIsCalibrated = ui_helper.drawState(
            frame, "Is camera calibrated: ", self.varIsCalibrated, "False"
        )
        stateIsCamReady = ui_helper.drawState(
            frame, "Is camera ready:", self.varIsCameraReady, "False"
        )

        btnRefresh = ui_helper.drawIconButton(
            frame, self.imgRefresh, self.refreshStatus
        )

        stateIsCalibrated.grid(row=0, column=0, pady=5)
        stateIsCamReady.grid(row=1, column=0, pady=5)
        btnRefresh.grid(row=2, column=0, pady=10)
        
        self.interactables.append(btnRefresh)

        frame.columnconfigure(index=0, weight=1)

        return frame

    def drawFrameTrackerLockSettings(self, parent):
        frame = ttk.LabelFrame(parent, text="Lock settings")

        labelPosition = ttk.Label(frame, text="Position")
        framePosition = ttk.Frame(frame)
        checkboxX = ui_helper.drawCheckBox(framePosition, "x", self.varLockX)
        checkboxY = ui_helper.drawCheckBox(framePosition, "y", self.varLockY)
        checkboxZ = ui_helper.drawCheckBox(framePosition, "z", self.varLockZ)
        checkboxX.grid(row=0, column=0, pady=5)
        checkboxY.grid(row=0, column=1, pady=5)
        checkboxZ.grid(row=0, column=2, pady=5)
        framePosition.columnconfigure(index=0, weight=1)
        framePosition.columnconfigure(index=1, weight=1)
        framePosition.columnconfigure(index=2, weight=1)

        labelRotation = ttk.Label(frame, text="Rotation")
        frameRotation = ttk.Frame(frame)
        checkboxRoll = ui_helper.drawCheckBox(frameRotation, "roll", self.varLockRoll)
        checkboxPitch = ui_helper.drawCheckBox(
            frameRotation, "pitch", self.varLockPitch
        )
        checkboxYaw = ui_helper.drawCheckBox(frameRotation, "yaw", self.varLockYaw)
        checkboxRoll.grid(row=0, column=0, pady=5)
        checkboxPitch.grid(row=0, column=1, pady=5)
        checkboxYaw.grid(row=0, column=2, pady=5)
        frameRotation.columnconfigure(index=0, weight=1)
        frameRotation.columnconfigure(index=1, weight=1)
        frameRotation.columnconfigure(index=2, weight=1)

        labelPosition.grid(row=0, column=0, pady=5)
        framePosition.grid(row=1, column=0, pady=5, sticky=tk.EW)
        labelRotation.grid(row=2, column=0, pady=5)
        frameRotation.grid(row=3, column=0, pady=5, sticky=tk.EW)

        frame.rowconfigure(index=0, weight=1)
        frame.rowconfigure(index=1, weight=1)
        frame.rowconfigure(index=2, weight=1)
        frame.rowconfigure(index=3, weight=1)
        frame.columnconfigure(index=0, weight=1)
        return frame

    def drawFrameTracker(self, parent):
        frame = ttk.Labelframe(parent, text="Tracker")

        frameStatus = self.drawFrameCalibratorStatus(frame)

        frameLockSettings = self.drawFrameTrackerLockSettings(frame)

        # fieldCameraIndex = ui_helper.drawTextField(
        #     frame, self.varCameraIndex, "Camera index", "0", 5
        # )
        frameCamera = ttk.Frame(frame)
        comboBoxCamera = ui_helper.drawComboBox(frameCamera, self.availableCameras, self.varSelectedCamera)
        btnRefresh = ui_helper.drawIconButton(frameCamera, self.imgRefresh, self.updateAvailableCameras)
        comboBoxCamera.grid(row=0, column=0, padx=5, pady=5)
        btnRefresh.grid(row=0, column=1, padx=5, pady= 5)
        frameCamera.columnconfigure(index=0, weight=1)
        
        self.interactables.append(comboBoxCamera)
        self.interactables.append(btnRefresh)
        
        self.comboBoxCamera = comboBoxCamera
        fieldWebocketIP, entryWebsocketIP = ui_helper.drawTextField(
            frame, self.varWebsocketIP, "Websocket IP", "ws://localhost:8090", 20
        )
        btnStartTracking = ui_helper.drawButton(
            frame, "Start Tracking", self.onClickStartTracking
        )
        
        self.interactables.append(entryWebsocketIP)
        self.interactables.append(btnStartTracking)

        frameStatus.grid(row=0, column=0, padx=10, pady=5, sticky=tk.EW)
        frameLockSettings.grid(row=1, column=0, padx=10, pady=5, sticky=tk.EW)
        frameCamera.grid(row=2, column=0, padx=10, pady=5)
        fieldWebocketIP.grid(row=3, column=0, padx=10, pady=5)
        btnStartTracking.grid(row=4, column=0, pady=5)

        frame.columnconfigure(index=0, weight=1)

        return frame

    def drawCubeStatus(self, parent, cubeIndex):
        frame = ttk.LabelFrame(parent, text=f"Cube {cubeIndex}", width=230, height=100)
        labelActiveID = ui_helper.drawStateUnpropagated(
            frame, "Active marker id", self.varCubeActiveMarkerIDs[cubeIndex], "-"
        )
        labelPosition = ui_helper.drawStateUnpropagated(
            frame, "Position", self.varCubePositions[cubeIndex], "[0; 0; 0]"
        )
        labelRotation = ui_helper.drawStateUnpropagated(
            frame, "Rotation", self.varCubeRotations[cubeIndex], "[0; 0; 0]"
        )

        labelActiveID.configure(width=220)
        labelPosition.configure(width=220)
        labelRotation.configure(width=220)
        labelActiveID.grid(row=0, column=0, ipadx=5, pady=10)
        labelPosition.grid(row=1, column=0, ipadx=5, pady=5)
        labelRotation.grid(row=2, column=0, ipadx=5, pady=5)

        frame.columnconfigure(index=0, weight=1)
        frame.grid_propagate(False)
        return frame

    def drawFrameTrackingInspector(self, parent):
        frame = ttk.LabelFrame(parent, text="Tracking Inspector")

        for index in range(6):
            status_cube = self.drawCubeStatus(frame, index)
            status_cube.grid(
                row=int(index / 3),
                column=int(index % 3),
                ipadx=10,
                ipady=10,
                padx=10,
                pady=10,
            )
            pass

        frame.rowconfigure(index=0, weight=1)
        frame.rowconfigure(index=1, weight=1)
        frame.rowconfigure(index=2, weight=1)
        frame.columnconfigure(index=0, weight=1)
        frame.columnconfigure(index=1, weight=1)
        frame.columnconfigure(index=2, weight=1)

        return frame

    def run(self):
        # self.update_frame()
        self.mainwindow.mainloop()
        pass

    def updateFrame(self):
        self.mainwindow.after(1000, self.updateFrame)
        pass
    
    def updateAvailableCameras(self):
        self.availableCameras = helper.getAvailableCameras()
        defaultCamName = ""
        
        if len(self.availableCameras) > 0:
            defaultCamName = self.availableCameras[0]
            
        # self.varCameraIndex.set(0)
        self.varSelectedCamera.set(defaultCamName)
        
        self.comboBoxCamera.configure(values=self.availableCameras)
        pass
    
    def onNewCameraSelected(self, var, index, mode):
        print(f"Camera {self.varSelectedCamera.get()} is selected. Set index to {self.comboBoxCamera.current()}")
        self.varCameraIndex.set(self.comboBoxCamera.current())
        self.refreshStatus()
        pass

    def onClickGenerateAruco(self):
        generator.generatePackedArucoMarkers(
            markerFolder=MARKER_FOLDER,
            packedFolder=PACKED_FOLDER,
            arucoDict=ARUCO_DICT,
            numMarkers=36,
            markerSizecm=float(self.varArucoSize.get()),
            gapSizecm=float(self.varArucoGapSize.get()),
        )
        showinfo(
            title="Generate Aruco Markers",
            message=f"Successfully generated aruco markers. \n The files are at: {PACKED_FOLDER}",
        )
        pass

    def onClickGenerateCharucoBoard(self):
        generator.generateCharucoBoard(
            outputFolder=CHARUCO_FOLDER,
            arucoDict=ARUCO_DICT,
            pattern=CHARUCO_BOARD_PATTERN,
            markerSizecm=float(self.varArucoSize.get()),
            gapSizecm=float(self.varArucoGapSize.get()),
        )
        showinfo(
            title="Generate Aruco Board",
            message=f"Successfully generated aruco board. \n The files are at: {CHARUCO_FOLDER}",
        )
        pass

    def onClickCalibrateCamera(self):
        self.refreshStatus()
        if self.varIsCameraReady.get() == "False":
            showerror(
                title="Camera is not found",
                message=f"Please check if your camera is connect.",
            )
            return
        self.calibrationThread = Thread(
            target=self.calibrator.startCalibration
        )
        self.calibrationThread.start()
        self.disableButtons()
        pass

    def onClickStartTracking(self):
        print("Try start tracking")
        if self.trackingThread != None and self.trackingThread.is_alive():
            showinfo(
                title="Tracker is running already",
                message=f"Tracker is running already. Please press Q in Tracker window to close it.",
            )
            return
        if self.isTrackerReady() is False:
            showinfo(
                title="Tracker is not ready",
                message=f"Tracker is not ready yet. Please check status panel.",
            )
            return
        ip = self.varWebsocketIP.get()
        calibFilePath = os.path.join(CALIB_FOLDER, "calib.npz")
        self.trackingThread = Thread(
            target=self.tracker.startTrackingMarkers,
            args=(calibFilePath, ip, self.varCameraIndex.get()),
        )
        # run tracking in different threads
        self.trackingThread.start()
        self.disableButtons()
        pass

    def refreshStatus(self):
        calibFilePath = os.path.join(CALIB_FOLDER, "calib.npz")

        self.varIsCalibrated.set(str(helper.isFileExit(calibFilePath)))
        self.varIsCameraReady.set(
            str(helper.isCameraAvailable(self.varCameraIndex.get()))
        )
        pass

    def isTrackerReady(self):
        self.refreshStatus()
        if self.varIsCalibrated.get() == "False":
            return False
        if self.varIsCameraReady.get() == "False":
            return False
        return True

    def onRootWindowClose(self):
        self.tracker.terminate()
        self.mainwindow.destroy()
        pass

    def onTrack(self, markerIds, positions, rotations):
        if len(markerIds) == 0:
            for index in range(6):
                self.varCubeActiveMarkerIDs[index].set("-")
                self.varCubePositions[index].set(f"[0; 0; 0]")
                self.varCubeRotations[index].set(f"[0; 0; 0]")
            pass
        else:
            for index in range(6):
                if markerIds[index] > -1:
                    p = positions[index]
                    r = rotations[index]

                    self.varCubeActiveMarkerIDs[index].set(str(markerIds[index]))
                    self.varCubePositions[index].set(
                        f"[{helper.format(p[0][0])}; {helper.format(p[1][0])}; {helper.format(p[2][0])}]"
                    )
                    self.varCubeRotations[index].set(
                        f"[{helper.format(r[0])}; {helper.format(r[1])}; {helper.format(-r[2])}]"
                    )
                else:
                    self.varCubeActiveMarkerIDs[index].set("-")
                    self.varCubePositions[index].set(f"[0; 0; 0]")
                    self.varCubeRotations[index].set(f"[0; 0; 0]")
            pass
        pass
    
    def onTrackingFinish(self):
        print("tracker is closed now.")
        if self.tracker.forceTerminate == False:
            self.enableButtons()
        pass
    
    def onTrackingFail(self, reason):
        showerror(
            title="Tracking Failed",
            message=f"Tracking failed. Reason: {reason}"
        )
        self.enableButtons()
        pass

    def onCalibrationFinish(self):
        showinfo(
            title="Calibration Success",
            message=f"Camera is successfully calibrated. Now you can start tracking!",
        )
        self.refreshStatus()
        self.enableButtons()
        pass
    
    def onCalibrationFail(self, reason):
        showerror(
            title="Calibration Failed",
            message=f"Camera calibration failed. Reason: {reason}"
        )
        self.enableButtons()
        pass

if __name__ == "__main__":
    app = VreactableApp()
    app.run()
    if app.trackingThread != None:
        app.trackingThread.join()
