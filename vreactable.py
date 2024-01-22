import pathlib
from tkinter.messagebox import showerror, showwarning, showinfo
from camera_calibrator import sample_image_capturer, calibrator
import cv2.aruco as aruco
from detector import detector
from aruco_generators import generator
from helper import helper
import pathlib
import os
import configparser
config = configparser.ConfigParser()
config.read('./config.ini')

from ttkbootstrap import Style
import tkinter as tk
from tkinter import ttk

MARKER_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['MarkerFolder'])
PACKED_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['PackedFolder'])
CHARUCO_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['CharucoFolder'])
SAMPLE_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['SampleFolder'])
CALIB_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['CalibFolder'])

ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)

class VreactableApp:
    def __init__(self, master=None):
        # build ui
        style = Style(theme='darkly')
        self.toplevel_vreactable = style.master
        self.toplevel_vreactable.configure(height=700, width=600)
        self.toplevel_vreactable.minsize(0, 200)
        self.toplevel_vreactable.title("VRectable")
        
        self.frame_vreactable = ttk.Frame(self.toplevel_vreactable)
        self.frame_vreactable.configure(height=200, width=400)
        
        # title
        self.frame_title = ttk.Frame(self.frame_vreactable)
        self.label_title = ttk.Label(self.frame_title)
        self.label_title.configure(text='VReactable')
        self.label_title.pack(side="top")
        self.frame_title.pack(
            expand=False,
            fill="x",
            padx=20,
            pady=10,
            side="top")
        
        # main frame
        self.frame_container = ttk.Frame(self.frame_vreactable)
        self.frame_container.configure(height=200, width=200)
        self.frame_left = ttk.Frame(self.frame_container)
        self.frame_left.configure(height=200, width=300)
        
        # aruco generator
        self.draw_aruco_generator_frame()
        # calibration fraem
        self.frame_calibration = ttk.Labelframe(self.frame_left)
        self.frame_calibration.configure(text='Calibration', width=200)
        self.frame_board_settings = ttk.Labelframe(self.frame_calibration)
        self.frame_board_settings.configure(
            height=100, text='CharucoBoard Settings', width=200)
        frame4 = ttk.Frame(self.frame_board_settings)
        frame4.configure(height=200, width=200)
        label4 = ttk.Label(frame4)
        label4.configure(text='Pattern')
        label4.grid(column=0, row=0)
        self.frame_pattern = ttk.Frame(frame4)
        self.frame_pattern.configure(height=200, width=200)
        self.entry_row = ttk.Entry(self.frame_pattern)
        self.var_board_pattern_row = tk.StringVar(value='5')
        self.entry_row.configure(
            justify="center",
            textvariable=self.var_board_pattern_row,
            width=3)
        _text_ = '5'
        self.entry_row.delete("0", "end")
        self.entry_row.insert("0", _text_)
        self.entry_row.grid(column=0, row=0)
        self.label_x = ttk.Label(self.frame_pattern)
        self.label_x.configure(text='x')
        self.label_x.grid(column=1, row=0)
        self.entry_column = ttk.Entry(self.frame_pattern)
        self.var_board_pattern_column = tk.StringVar(value='7')
        self.entry_column.configure(
            justify="center",
            textvariable=self.var_board_pattern_column,
            width=3)
        _text_ = '7'
        self.entry_column.delete("0", "end")
        self.entry_column.insert("0", _text_)
        self.entry_column.grid(column=2, row=0)
        self.frame_pattern.grid(column=1, padx=10, row=0)
        frame4.pack(pady=10, side="top")
        self.button_generate_charuco_board = ttk.Button(
            self.frame_board_settings)
        self.button_generate_charuco_board.configure(
            text='Generate charuco board')
        self.button_generate_charuco_board.pack(ipadx=20, pady=10, side="top")
        self.button_generate_charuco_board.configure(
            command=self.on_click_generate_charuco_board)
        self.frame_board_settings.pack(
            expand=True, fill="x", padx=20, pady=10, side="top")
        self.frame_sample_images_count = ttk.Frame(self.frame_calibration)
        self.frame_sample_images_count.configure(height=200, width=200)
        self.frame2 = ttk.Frame(self.frame_sample_images_count)
        self.frame2.configure(height=200, width=200)
        self.label1 = ttk.Label(self.frame2)
        self.label1.configure(
            compound="center",
            justify="center",
            padding=10,
            text='Sampled image count:')
        self.label1.pack()
        self.frame2.grid(column=0, row=0)
        self.frame3 = ttk.Frame(self.frame_sample_images_count)
        self.frame3.configure(height=200, width=200)
        self.label2 = ttk.Label(self.frame3)
        self.var_sample_image_count = tk.StringVar(value='0')
        self.label2.configure(
            text='0', textvariable=self.var_sample_image_count)
        self.label2.pack()
        self.frame3.grid(column=1, row=0)
        self.btn_referesh = ttk.Button(self.frame_sample_images_count)
        self.img_refresh = tk.PhotoImage(file="assets/refresh.png")
        self.btn_referesh.configure(image=self.img_refresh)
        self.btn_referesh.grid(column=2, padx=10, row=0)
        self.btn_referesh.configure(
            command=self.on_click_refresh_sampled_count)
        self.frame_sample_images_count.pack(
            expand=True, fill="x", padx=10, pady=0, side="top")
        self.frame_sample_images_count.grid_anchor("center")
        self.button_sample_images = ttk.Button(self.frame_calibration)
        self.button_sample_images.configure(text='Capture sample images')
        self.button_sample_images.pack(ipadx=20, pady=10, side="top")
        self.button_sample_images.configure(
            command=self.on_click_capture_sample_images)
        self.frame_is_calibrated = ttk.Frame(self.frame_calibration)
        self.frame_is_calibrated.configure(height=200, width=200)
        self.frame_is_calibrated_l = ttk.Frame(self.frame_is_calibrated)
        self.frame_is_calibrated_l.configure(height=200, width=200)
        self.label_is_calibrated = ttk.Label(self.frame_is_calibrated_l)
        self.label_is_calibrated.configure(
            compound="center",
            justify="center",
            padding=10,
            text='Is Calibrated:')
        self.label_is_calibrated.pack()
        self.frame_is_calibrated_l.grid(column=0, row=0)
        self.frame_is_calibrated_r = ttk.Frame(self.frame_is_calibrated)
        self.frame_is_calibrated_r.configure(height=200, width=200)
        self.label_is_calibrated_value = ttk.Label(self.frame_is_calibrated_r)
        self.var_is_calibrated = tk.StringVar(value='Yes')
        self.label_is_calibrated_value.configure(
            text='Yes', textvariable=self.var_is_calibrated)
        self.label_is_calibrated_value.pack()
        self.frame_is_calibrated_r.grid(column=1, row=0)
        self.frame_is_calibrated.pack(
            expand=True, fill="x", padx=10, pady=0, side="top")
        self.frame_is_calibrated.grid_anchor("center")
        self.button_calibrate = ttk.Button(self.frame_calibration)
        self.button_calibrate.configure(text='Calibrate camera')
        self.button_calibrate.pack(ipadx=20, pady=10, side="top")
        self.button_calibrate.configure(command=self.on_click_calibrate_camera)
        self.frame_calibration.pack(
            expand=False, fill="x", padx=20, pady=5, side="top")
        self.frame_left.grid(column=0, row=0)
        self.frame_right = ttk.Frame(self.frame_container)
        self.frame_right.configure(height=200, width=200)
        self.frame_status = ttk.Labelframe(self.frame_right)
        self.frame_status.configure(height=200, text='Status', width=200)
        frame12 = ttk.Frame(self.frame_status)
        frame12.configure(height=200, width=200)
        self.label11 = ttk.Label(frame12)
        self.label11.configure(text='Is Calibrated:')
        self.label11.grid(column=0, row=0)
        self.label12 = ttk.Label(frame12)
        self.var_is_detection_ready = tk.StringVar(value='Yes')
        self.label12.configure(text='Yes',
                               textvariable=self.var_is_detection_ready)
        self.label12.grid(column=1, padx=10, row=0)
        frame12.pack(ipadx=10, side="top")
        frame13 = ttk.Frame(self.frame_status)
        frame13.configure(height=200, width=200)
        self.label13 = ttk.Label(frame13)
        self.label13.configure(text='Is Camera ready:')
        self.label13.grid(column=0, row=0)
        self.label14 = ttk.Label(frame13)
        self.label14.configure(text='Yes',
                               textvariable=self.var_is_detection_ready)
        self.label14.grid(column=1, padx=10, row=0)
        frame13.pack(ipadx=10, side="top")
        self.frame_status.pack(
            fill="x",
            ipady=10,
            padx=10,
            pady=10,
            side="top")
        self.label_frame_detect = ttk.Labelframe(self.frame_right)
        self.label_frame_detect.configure(
            height=200, text='Detection', width=200)
        frame10 = ttk.Frame(self.label_frame_detect)
        frame10.configure(height=200, width=200)
        self.label_detection_ready = ttk.Label(frame10)
        self.label_detection_ready.configure(text='Is Detection Ready:')
        self.label_detection_ready.grid(column=0, row=0)
        self.label_is_detection_ready = ttk.Label(frame10)
        self.label_is_detection_ready.configure(
            text='Yes', textvariable=self.var_is_detection_ready)
        self.label_is_detection_ready.grid(column=1, padx=10, row=0)
        frame10.pack(ipadx=10, pady=10, side="top")
        frame14 = ttk.Frame(self.label_frame_detect)
        frame14.configure(height=200, width=200)
        self.label15 = ttk.Label(frame14)
        self.label15.configure(text='Websocket IP:')
        self.label15.grid(column=0, row=0)
        self.entry_websocket_ip = ttk.Entry(frame14)
        self.var_websocket_ip = tk.StringVar(value='ws://localhost:8090')
        self.entry_websocket_ip.configure(textvariable=self.var_websocket_ip)
        _text_ = 'ws://localhost:8090'
        self.entry_websocket_ip.delete("0", "end")
        self.entry_websocket_ip.insert("0", _text_)
        self.entry_websocket_ip.grid(column=1, padx=10, row=0)
        frame14.pack(ipadx=10, pady=10, side="top")
        self.button_detect = ttk.Button(self.label_frame_detect)
        self.button_detect.configure(text='Detect')
        self.button_detect.pack(ipadx=30, ipady=2, pady=10, side="top")
        self.button_detect.configure(command=self.on_click_detect)
        self.label_frame_detect.pack(
            expand=True, fill="both", padx=10, side="top")
        self.frame_right.grid(column=1, padx=10, row=0)
        self.frame_container.pack(
            expand=False, fill="both", padx=20, side="top")
        self.frame_container.columnconfigure(0, weight=2)
        self.frame_container.columnconfigure(1, weight=1)
        self.frame_vreactable.pack(expand=True, fill="both", side="top")
        self.frame_vreactable.pack_propagate(0)
        self.toplevel_vreactable.pack_propagate(0)

        # Main widget
        self.mainwindow = self.toplevel_vreactable
        
    def draw_number_field(self, parent, variable: tk.StringVar, title: str, default_value: str):
        num_field = ttk.Frame(parent)
        num_field.configure(height=200, width=200)
        field_title = ttk.Label(num_field)
        field_title.configure(text=title)
        field_title.grid(column=0, row=0)
        entry = ttk.Entry(num_field)
        entry.configure(
            justify="center", textvariable=variable, width=5)
        entry.delete("0", "end")
        entry.insert("0", default_value)
        entry.grid(column=1, padx=10, row=0)
        num_field.pack(pady=10, side="top")
        pass
    
    def draw_cm_number_field(self, parent, variable: tk.StringVar, title: str, default_value: str):
        cm_num_field = ttk.Frame(parent)
        cm_num_field.configure(height=200, width=200)
        field_title = ttk.Label(cm_num_field)
        field_title.configure(text=title)
        field_title.grid(column=0, row=0)
        entry = ttk.Entry(cm_num_field)
        entry.configure(
            justify="center",
            textvariable=variable,
            validate="focusout",
            width=5)
        entry.delete("0", "end")
        entry.insert("0", default_value)
        entry.grid(column=1, padx=10, row=0)
        text_cm = ttk.Label(cm_num_field)
        text_cm.configure(text='cm')
        text_cm.grid(column=2, row=0)
        cm_num_field.pack(pady=10, side="top")
        
    def draw_button(self, parent, title, callback):
        self.button_generate_aruco = ttk.Button(parent)
        self.button_generate_aruco.configure(text=title)
        self.button_generate_aruco.pack(ipadx=10, pady=10, side="top")
        self.button_generate_aruco.configure(command = callback)
        
    def draw_aruco_generator_frame(self):
        # aruco generator
        self.frame_aruco_generator = ttk.Labelframe(self.frame_left)
        self.frame_aruco_generator.configure(
            height=200, text='Aruco Generator', width=200)
        self.var_num_of_markers = tk.StringVar(value='36')
        self.draw_number_field(self.frame_aruco_generator, self.var_num_of_markers, "Num of markers", '36')
        self.var_aruco_size = tk.StringVar(value='5')
        self.draw_cm_number_field(self.frame_aruco_generator, self.var_aruco_size, "Marker size", '5')
        self.var_aruco_gap_size = tk.StringVar(value='0.5')
        self.draw_cm_number_field(self.frame_aruco_generator, self.var_aruco_gap_size, "Gap size", '0.5')
        self.draw_button(self.frame_aruco_generator, 'Generate aruco markers', self.on_click_generate_aruco)
        self.frame_aruco_generator.pack(
            expand=False, fill="x", padx=20, pady=5, side="top")

    def run(self):
        self.mainwindow.mainloop()

    def on_click_generate_aruco(self):
        generator.generatePackedArucoMarkers(
        markerFolder = MARKER_FOLDER,
        packedFolder = PACKED_FOLDER,
        arucoDict = ARUCO_DICT,
        numMarkers = int(self.var_num_of_markers.get()),
        markerSizecm = float(self.var_aruco_size.get()),
        gapSizecm = float(self.var_aruco_gap_size.get()))
        showinfo(title = 'Generate Aruco Markers', message = f'Successfully generated aruco markers. \n The files are at: {PACKED_FOLDER}')
        pass

    def on_click_generate_charuco_board(self):
        pattern = (
            int(self.var_board_pattern_row.get()),
            int(self.var_board_pattern_column.get())
        )
        generator.generateCharucoBoard(outputFolder = CHARUCO_FOLDER, arucoDict = ARUCO_DICT, pattern = pattern, markerSizecm = float(self.var_aruco_size.get()), gapSizecm = float(self.var_aruco_gap_size.get()))
        showinfo(title = 'Generate Aruco Board', message = f'Successfully generated aruco board. \n The files are at: {CHARUCO_FOLDER}')
        pass

    def on_click_refresh_sampled_count(self):
        numImgs = helper.countImages(SAMPLE_FOLDER)
        self.var_sample_image_count.set(str(numImgs))
        pass

    def on_click_capture_sample_images(self):
        sample_image_capturer.capture_sample_images(SAMPLE_FOLDER)
        self.updateNumSampledImages()
        showinfo(title = 'Capture Sample Images', message = f'Successfully sampled images. \n The files are at: {SAMPLE_FOLDER}')
        pass

    def on_click_calibrate_camera(self):
        pattern = (
            int(self.var_board_pattern_row.get()),
            int(self.var_board_pattern_column.get())
        )
        calibrator.calibrate(
            sampleFolder = SAMPLE_FOLDER, calibFolder = CALIB_FOLDER, 
            arucoDict = ARUCO_DICT, pattern = pattern)
        self.updateIsCalibrated()
        pass

    def on_click_detect(self):
        print("Start detecting")
        ip = self.var_websocket_ip.get()
        calibFilePath = f'{pathlib.Path().resolve()}/resources/calib.npz'
        detector.detect_arucos(calibFilePath, ip)
        pass


if __name__ == "__main__":
    app = VreactableApp()
    app.run()