import pathlib
from tkinter.messagebox import showerror, showwarning, showinfo
from camera_calibrator import sample_image_capturer, calibrator
import cv2.aruco as aruco
from detector import detector
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


class VreactableApp:
    def __init__(self, master=None):
        # build ui
        style = Style(theme="darkly")
        self.toplevel_vreactable = style.master
        # self.toplevel_vreactable.configure(height=700, width=600)
        # self.toplevel_vreactable.minsize(700, 600)
        self.toplevel_vreactable.title("VRectable")
        self.frame_main = ttk.Frame(self.toplevel_vreactable)
        self.frame_main.grid(row=0, column=0, padx=20, pady=10, sticky=tk.NSEW)

        self.img_refresh = tk.PhotoImage(file="assets/refresh.png")

        # title
        frame_header = ttk.Frame(self.frame_main)
        label_title = ttk.Label(frame_header)
        label_title.configure(text="VReactable")
        label_title.grid(row=0, column=0, pady=5)
        frame_header.grid(row=0, column=0, padx=10)

        # main frame
        frame_body = ttk.Frame(self.frame_main)

        # left frame
        frame_left = ttk.Frame(frame_body)
        frame_aruco_generator = self.draw_frame_aruco_generator(frame_left)
        frame_calibration = self.draw_frame_calibration(frame_left)
        # organize layout
        frame_aruco_generator.grid(
            row=0, column=0, ipadx=15, ipady=5, pady=10, sticky=tk.EW
        )
        frame_calibration.grid(row=1, column=0, ipadx=15, ipady=5, pady=1, sticky=tk.EW)
        frame_left.grid(row=0, column=0, padx=10)
        frame_left.columnconfigure(0, weight=1)

        # right frame
        frame_right = ttk.Frame(frame_body)
        frame_status = self.draw_status_frame(frame_right)
        frame_detect = self.draw_detection_frame(frame_right)
        frame_status.grid(row=0, column=0, ipadx=10, ipady=10, pady=10, sticky=tk.EW)
        frame_detect.grid(row=1, column=0, ipadx=10, ipady=10, pady=10, sticky=tk.EW)
        frame_right.grid(row=0, column=1, padx=10)
        frame_right.columnconfigure(0, weight=1)

        frame_body.grid(row=1, column=0, pady=5)
        frame_body.columnconfigure(0, weight=2)
        frame_body.columnconfigure(1, weight=1)

        # Main widget
        self.mainwindow = self.toplevel_vreactable

    def draw_frame_aruco_generator(self, parent):
        # aruco generator
        frame = ttk.Labelframe(parent, text="Aruco Generator")
        self.var_num_of_markers = tk.StringVar(value="36")
        self.var_aruco_size = tk.StringVar(value="5")
        self.var_aruco_gap_size = tk.StringVar(value="0.5")

        text_field_marker = ui_helper.draw_text_field(
            frame, self.var_num_of_markers, "Num of markers", "36"
        )
        text_field_marker_size = ui_helper.draw_cm_number_field(
            frame, self.var_aruco_size, "Marker size", "5"
        )
        text_field_gap_size = ui_helper.draw_cm_number_field(
            frame, self.var_aruco_gap_size, "Gap size", "0.5"
        )
        btn_generate = ui_helper.draw_button(
            frame, "Generate aruco markers", self.on_click_generate_aruco
        )

        text_field_marker.grid(row=0, column=0, pady=5)
        text_field_marker_size.grid(row=1, column=0, pady=5)
        text_field_gap_size.grid(row=2, column=0, pady=5)
        btn_generate.grid(row=3, column=0, ipadx=10, pady=5)

        frame.columnconfigure(0, weight=1)
        return frame

    def draw_frame_calibration_settings(self, parent):
        frame = ttk.Labelframe(parent, text="CharucoBoard Settings")
        self.var_board_pattern_row = tk.StringVar(value="5")
        self.var_board_pattern_column = tk.StringVar(value="7")

        charuco_pattern_field = ui_helper.draw_charuco_pattern_field(
            frame,
            self.var_board_pattern_row,
            self.var_board_pattern_column,
            "Pattern",
            "5",
            "7",
        )
        btn_generate = ui_helper.draw_button(
            frame, "Generate charuco board", self.on_click_generate_charuco_board
        )

        charuco_pattern_field.grid(row=0, column=0, pady=5)
        btn_generate.grid(row=1, column=0, pady=5)

        frame.columnconfigure(index=0, weight=1)

        return frame

    def draw_frame_calibration(self, parent):
        frame = ttk.Labelframe(parent, text="Calibration")
        self.var_sample_image_count = tk.StringVar(value="0")

        frame_settings = self.draw_frame_calibration_settings(frame)

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

        frame_settings.grid(row=0, column=0, ipadx=10, ipady=10, pady=5)
        rs_field_sample_count.grid(row=1, column=0, pady=5)
        btn_capture.grid(row=2, column=0, pady=5)
        btn_calibrate.grid(row=3, column=0, pady=5)
        frame.columnconfigure(index=0, weight=1)

        return frame

    def draw_status_frame(self, parent):
        frame = ttk.Labelframe(parent, text="Status")
        self.var_is_calibrated = tk.StringVar(value="No")
        self.var_is_camera_ready = tk.StringVar(value="No")

        s_field_is_calibrated = ui_helper.draw_state_field(
            frame, "Is Calibrated: ", self.var_is_calibrated, "No"
        )
        s_field_is_cam_ready = ui_helper.draw_state_field(
            frame, "Is Camera ready:", self.var_is_camera_ready, "No"
        )

        btn_refresh = ui_helper.draw_icon_button(
            frame, self.img_refresh, self.refresh_status
        )

        s_field_is_calibrated.grid(row=0, column=0, pady=5)
        s_field_is_cam_ready.grid(row=1, column=0, pady=5)
        btn_refresh.grid(row=2, column=0, pady=5)

        frame.columnconfigure(index=0, weight=1)

        return frame

    def draw_detection_frame(self, parent):
        frame = ttk.Labelframe(parent, text="Detection")
        self.var_websocket_ip = tk.StringVar(value="ws://localhost:8090")

        field_webocket_ip = ui_helper.draw_text_field(
            frame, self.var_websocket_ip, "Websocket IP", "ws://localhost:8090", 20
        )
        btn_detect = ui_helper.draw_button(frame, "Detect", self.on_click_detect)

        field_webocket_ip.grid(row=0, column=0, padx=10, pady=5)
        btn_detect.grid(row=1, column=0, pady=5)

        frame.columnconfigure(index=0, weight=1)

        return frame

    def run(self):
        self.mainwindow.mainloop()
        pass

    def on_click_generate_aruco(self):
        generator.generatePackedArucoMarkers(
            markerFolder=MARKER_FOLDER,
            packedFolder=PACKED_FOLDER,
            arucoDict=ARUCO_DICT,
            numMarkers=int(self.var_num_of_markers.get()),
            markerSizecm=float(self.var_aruco_size.get()),
            gapSizecm=float(self.var_aruco_gap_size.get()),
        )
        showinfo(
            title="Generate Aruco Markers",
            message=f"Successfully generated aruco markers. \n The files are at: {PACKED_FOLDER}",
        )
        pass

    def on_click_generate_charuco_board(self):
        pattern = (
            int(self.var_board_pattern_row.get()),
            int(self.var_board_pattern_column.get()),
        )
        generator.generateCharucoBoard(
            outputFolder=CHARUCO_FOLDER,
            arucoDict=ARUCO_DICT,
            pattern=pattern,
            markerSizecm=float(self.var_aruco_size.get()),
            gapSizecm=float(self.var_aruco_gap_size.get()),
        )
        showinfo(
            title="Generate Aruco Board",
            message=f"Successfully generated aruco board. \n The files are at: {CHARUCO_FOLDER}",
        )
        pass

    def on_click_refresh_sampled_count(self):
        numImgs = helper.countImages(SAMPLE_FOLDER)
        self.var_sample_image_count.set(str(numImgs))
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
        pattern = (
            int(self.var_board_pattern_row.get()),
            int(self.var_board_pattern_column.get()),
        )
        calibrator.calibrate(
            sampleFolder=SAMPLE_FOLDER,
            calibFolder=CALIB_FOLDER,
            arucoDict=ARUCO_DICT,
            pattern=pattern,
        )
        self.refresh_status()
        pass

    def on_click_detect(self):
        print("Start detecting")
        ip = self.var_websocket_ip.get()
        calibFilePath = f"{pathlib.Path().resolve()}\\resources\\clibration\\calib.npz"
        detector.detect_arucos(calibFilePath, ip)
        pass

    def update_num_sampled_images():
        pass

    def refresh_status(self):
        pass


if __name__ == "__main__":
    app = VreactableApp()
    app.run()
