import pathlib
from tkinter.messagebox import showerror, showwarning, showinfo
from camera_calibrator import sample_image_capturer, calibrator
import cv2.aruco as aruco
from detector.detector import CubeDetector
from aruco_generators import generator
from helper import helper, ui_helper
import pathlib
import os
import configparser

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


class VreactableApp:
    def __init__(self, master=None):
        self.detector = CubeDetector(self.detect_callback)
        # build ui
        style = Style(theme="darkly")
        self.toplevel_vreactable = style.master
        # self.toplevel_vreactable.configure(height=700, width=600)
        # self.toplevel_vreactable.minsize(700, 600)
        self.toplevel_vreactable.title("VRectable")
        self.frame_main = ttk.Frame(self.toplevel_vreactable)
        self.frame_main.grid(row=0, column=0, padx=20, pady=10, sticky=tk.NSEW)

        self.img_refresh = tk.PhotoImage(file="assets/refresh.png")

        self.var_aruco_size = tk.StringVar(value="5")
        self.var_aruco_gap_size = tk.StringVar(value="0.5")
        self.var_sample_image_count = tk.StringVar(value="0")
        self.var_camera_index = tk.IntVar(value=0)
        self.var_websocket_ip = tk.StringVar(value="ws://localhost:8090")
        self.var_lock_x = tk.BooleanVar(value=False)
        self.var_lock_y = tk.BooleanVar(value=False)
        self.var_lock_z = tk.BooleanVar(value=False)
        self.var_lock_roll = tk.BooleanVar(value=False)
        self.var_lock_pitch = tk.BooleanVar(value=False)
        self.var_lock_yaw = tk.BooleanVar(value=False)

        self.var_cube_active_marker_ids = [tk.StringVar(value="-")] * 6
        self.var_cube_positions = [tk.StringVar(value="(0.00, 0.00, 0.00)")] * 6
        self.var_cube_rotations = [tk.StringVar(value="(0.00, 0.00, 0.00)")] * 6

        # title
        frame_header = ttk.Frame(self.frame_main)
        label_title = ttk.Label(frame_header)
        label_title.configure(text="VReactable")
        label_title.grid(row=0, column=0, pady=5)
        frame_header.grid(row=0, column=0, padx=10)
        self.var_is_calibrated = tk.StringVar(value="False")
        self.var_is_camera_ready = tk.StringVar(value="False")

        # main frame
        frame_body = ttk.Frame(self.frame_main)

        # frame 1
        frame_1 = ttk.Frame(frame_body)
        frame_aruco_generator = self.draw_frame_aruco_generator(frame_1)
        frame_calibration = self.draw_frame_calibration(frame_1)
        # organize layout
        frame_aruco_generator.grid(
            row=0, column=0, ipadx=15, ipady=5, pady=10, sticky=tk.EW
        )
        frame_calibration.grid(row=1, column=0, ipadx=15, ipady=5, pady=1, sticky=tk.EW)
        frame_1.grid(row=0, column=0, padx=10)
        frame_1.columnconfigure(0, weight=1)

        # frame 2
        frame_2 = ttk.Frame(frame_body)
        frame_detect = self.draw_frame_detector(frame_2)
        frame_detect.grid(row=0, column=0, ipadx=10, ipady=15, pady=10, sticky=tk.EW)
        frame_2.grid(row=0, column=1, padx=10)
        frame_2.columnconfigure(0, weight=1)

        # frame 3
        frame_3 = ttk.Frame(frame_body)
        frame_detection_inspector = self.draw_frame_detection_inspector(frame_3)
        frame_detection_inspector.grid(
            row=0, column=0, ipadx=10, ipady=15, pady=10, sticky=tk.EW
        )
        frame_3.grid(row=0, column=2, padx=10)
        frame_3.columnconfigure(0, weight=1)

        frame_body.grid(row=1, column=0, pady=5)
        frame_body.rowconfigure(0, weight=1)
        frame_body.columnconfigure(0, weight=2)
        frame_body.columnconfigure(1, weight=1)
        frame_body.columnconfigure(2, weight=2)

        # Main widget
        self.mainwindow = self.toplevel_vreactable

        self.update_num_sampled_images()
        self.refresh_status()

    def draw_frame_aruco_generator(self, parent):
        # aruco generator
        frame = ttk.Labelframe(parent, text="Aruco Generator")

        text_field_marker_size = ui_helper.draw_cm_number_field(
            frame, self.var_aruco_size, "Marker size", "5"
        )
        text_field_gap_size = ui_helper.draw_cm_number_field(
            frame, self.var_aruco_gap_size, "Gap size", "0.5"
        )
        btn_generate = ui_helper.draw_button(
            frame, "Generate aruco markers", self.on_click_generate_aruco
        )

        text_field_marker_size.grid(row=0, column=0, pady=5)
        text_field_gap_size.grid(row=1, column=0, pady=5)
        btn_generate.grid(row=2, column=0, ipadx=10, pady=5)

        frame.columnconfigure(0, weight=1)
        return frame

    def draw_frame_calibration(self, parent):
        frame = ttk.Labelframe(parent, text="Camera Calibratior")

        btn_generate = ui_helper.draw_button(
            frame, "Generate charuco board", self.on_click_generate_charuco_board
        )

        rs_field_sample_count = ui_helper.draw_refreshable_state_field(
            frame,
            "Sampled image count:",
            self.img_refresh,
            self.var_sample_image_count,
            "0",
            self.on_click_refresh_sampled_count,
        )
        btn_capture = ui_helper.draw_button(
            frame, "Capture sample images", self.on_click_capture_sample_images
        )
        btn_calibrate = ui_helper.draw_button(
            frame, "Calibrate camera", self.on_click_calibrate_camera
        )

        btn_generate.grid(row=0, column=0, pady=5)
        rs_field_sample_count.grid(row=1, column=0, pady=5)
        btn_capture.grid(row=2, column=0, pady=5)
        btn_calibrate.grid(row=3, column=0, pady=5)
        frame.columnconfigure(index=0, weight=1)

        return frame

    def draw_frame_status(self, parent):
        frame = ttk.Labelframe(parent, text="Status")

        s_field_is_calibrated = ui_helper.draw_state_label(
            frame, "Is camera calibrated: ", self.var_is_calibrated, "False"
        )
        s_field_is_cam_ready = ui_helper.draw_state_label(
            frame, "Is camera ready:", self.var_is_camera_ready, "False"
        )

        btn_refresh = ui_helper.draw_icon_button(
            frame, self.img_refresh, self.refresh_status
        )

        s_field_is_calibrated.grid(row=0, column=0, pady=5)
        s_field_is_cam_ready.grid(row=1, column=0, pady=5)
        btn_refresh.grid(row=2, column=0, pady=10)

        frame.columnconfigure(index=0, weight=1)

        return frame

    def draw_frame_detector_lock_settings(self, parent):
        frame = ttk.LabelFrame(parent, text="Lock settings")

        label_position = ttk.Label(frame, text="Position")
        frame_position = ttk.Frame(frame)
        checkbox_x = ui_helper.draw_check_box(frame_position, "x", self.var_lock_x)
        checkbox_y = ui_helper.draw_check_box(frame_position, "y", self.var_lock_y)
        checkbox_z = ui_helper.draw_check_box(frame_position, "z", self.var_lock_z)
        checkbox_x.grid(row=0, column=0, pady=5)
        checkbox_y.grid(row=0, column=1, pady=5)
        checkbox_z.grid(row=0, column=2, pady=5)
        frame_position.columnconfigure(index=0, weight=1)
        frame_position.columnconfigure(index=1, weight=1)
        frame_position.columnconfigure(index=2, weight=1)

        label_rotation = ttk.Label(frame, text="Rotation")
        frame_rotation = ttk.Frame(frame)
        checkbox_roll = ui_helper.draw_check_box(
            frame_rotation, "roll", self.var_lock_roll
        )
        checkbox_pitch = ui_helper.draw_check_box(
            frame_rotation, "pitch", self.var_lock_pitch
        )
        checkbox_yaw = ui_helper.draw_check_box(
            frame_rotation, "yaw", self.var_lock_yaw
        )
        checkbox_roll.grid(row=0, column=0, pady=5)
        checkbox_pitch.grid(row=0, column=1, pady=5)
        checkbox_yaw.grid(row=0, column=2, pady=5)
        frame_rotation.columnconfigure(index=0, weight=1)
        frame_rotation.columnconfigure(index=1, weight=1)
        frame_rotation.columnconfigure(index=2, weight=1)

        label_position.grid(row=0, column=0, pady=5)
        frame_position.grid(row=1, column=0, pady=5, sticky=tk.EW)
        label_rotation.grid(row=2, column=0, pady=5)
        frame_rotation.grid(row=3, column=0, pady=5, sticky=tk.EW)

        frame.rowconfigure(index=0, weight=1)
        frame.rowconfigure(index=1, weight=1)
        frame.rowconfigure(index=2, weight=1)
        frame.rowconfigure(index=3, weight=1)
        frame.columnconfigure(index=0, weight=1)
        return frame

    def draw_frame_detector(self, parent):
        frame = ttk.Labelframe(parent, text="Detector")

        frame_status = self.draw_frame_status(frame)

        frame_lock_settings = self.draw_frame_detector_lock_settings(frame)

        field_camera_index = ui_helper.draw_text_field(
            frame, self.var_camera_index, "Camera index", "0", 5
        )
        field_webocket_ip = ui_helper.draw_text_field(
            frame, self.var_websocket_ip, "Websocket IP", "ws://localhost:8090", 20
        )
        btn_detect = ui_helper.draw_button(frame, "Detect", self.on_click_detect)

        frame_status.grid(row=0, column=0, padx=10, pady=5, sticky=tk.EW)
        frame_lock_settings.grid(row=1, column=0, padx=10, pady=5, sticky=tk.EW)
        field_camera_index.grid(row=2, column=0, padx=10, pady=5)
        field_webocket_ip.grid(row=3, column=0, padx=10, pady=5)
        btn_detect.grid(row=4, column=0, pady=5)

        frame.columnconfigure(index=0, weight=1)

        return frame

    def draw_cube_status(self, parent, cube_index):
        frame = ttk.LabelFrame(parent, text=f"Cube {cube_index}")
        label_active_code = ui_helper.draw_state_label(
            frame, "Active marker id", self.var_cube_active_marker_ids[cube_index], "-"
        )
        label_position = ui_helper.draw_state_label(
            frame, "Position", self.var_cube_positions[cube_index], "(0.00, 0.00, 0.00)"
        )
        label_rotation = ui_helper.draw_state_label(
            frame, "Rotation", self.var_cube_rotations[cube_index], "(0.00, 0.00, 0.00)"
        )

        label_active_code.grid(row=0, column=0, ipadx=5, pady=10)
        label_position.grid(row=1, column=0, ipadx=5, pady=5)
        label_rotation.grid(row=2, column=0, ipadx=5, pady=5)

        frame.columnconfigure(index=0, weight=1)
        return frame

    def draw_frame_detection_inspector(self, parent):
        frame = ttk.LabelFrame(parent, text="Detection Inspector")

        for index in range(6):
            status_cube = self.draw_cube_status(frame, index)
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
        self.mainwindow.mainloop()
        pass

    def on_click_generate_aruco(self):
        generator.generatePackedArucoMarkers(
            markerFolder=MARKER_FOLDER,
            packedFolder=PACKED_FOLDER,
            arucoDict=ARUCO_DICT,
            numMarkers=36,
            markerSizecm=float(self.var_aruco_size.get()),
            gapSizecm=float(self.var_aruco_gap_size.get()),
        )
        showinfo(
            title="Generate Aruco Markers",
            message=f"Successfully generated aruco markers. \n The files are at: {PACKED_FOLDER}",
        )
        pass

    def on_click_generate_charuco_board(self):
        generator.generateCharucoBoard(
            outputFolder=CHARUCO_FOLDER,
            arucoDict=ARUCO_DICT,
            pattern=CHARUCO_BOARD_PATTERN,
            markerSizecm=float(self.var_aruco_size.get()),
            gapSizecm=float(self.var_aruco_gap_size.get()),
        )
        showinfo(
            title="Generate Aruco Board",
            message=f"Successfully generated aruco board. \n The files are at: {CHARUCO_FOLDER}",
        )
        pass

    def on_click_refresh_sampled_count(self):
        self.update_num_sampled_images()
        pass

    def on_click_capture_sample_images(self):
        sample_image_capturer.capture_sample_images(SAMPLE_FOLDER)
        self.update_num_sampled_images()
        showinfo(
            title="Capture Sample Images",
            message=f"Successfully sampled images. \n The files are at: {SAMPLE_FOLDER}",
        )
        pass

    def on_click_calibrate_camera(self):
        calibrator.calibrate(
            sampleFolder=SAMPLE_FOLDER,
            calibFolder=CALIB_FOLDER,
            arucoDict=ARUCO_DICT,
            pattern=CHARUCO_BOARD_PATTERN,
        )
        self.refresh_status()
        pass

    def on_click_detect(self):
        print("Try start detecting")
        if self.is_detector_ready() is False:
            showinfo(
                title="Detector is not ready",
                message=f"Detector is not ready yet. Please check status panel.",
            )
            return
        ip = self.var_websocket_ip.get()
        calibFilePath = os.path.join(CALIB_FOLDER, "calib.npz")
        self.detector.detect_arucos(calibFilePath, ip)
        pass

    def update_num_sampled_images(self):
        numImgs = helper.countImages(SAMPLE_FOLDER)
        self.var_sample_image_count.set(str(numImgs))
        pass

    def refresh_status(self):
        calibFilePath = os.path.join(CALIB_FOLDER, "calib.npz")

        self.var_is_calibrated.set(str(helper.isFileExit(calibFilePath)))
        self.var_is_camera_ready.set(
            str(helper.isCameraAvailable(self.var_camera_index.get()))
        )
        pass

    def is_detector_ready(self):
        if self.var_is_calibrated.get() == "False":
            return False
        if self.var_is_camera_ready.get() == "False":
            return False
        return True

    def detect_callback(self, markerIds, positions, rotations):
        if len(markerIds) == 0:
            return

        for index in range(6):
            if markerIds[index] < 0:
                continue
            p = positions[index]
            r = rotations[index]

            self.var_cube_active_marker_ids[index].set(str(markerIds[index]))
            self.var_cube_positions[index].set(
                f"[{helper.format(p[0])};{helper.format(p[1])};{helper.format(p[2])}]"
            )
            self.var_cube_rotations[index].set(
                f"[{helper.format(r[0])};{helper.format(r[1])};{helper.format(-r[2])}]"
            )
        pass


if __name__ == "__main__":
    app = VreactableApp()
    app.run()
