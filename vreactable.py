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
        
        # left frame
        self.frame_left = ttk.Frame(self.frame_container)
        self.frame_left.configure(height=200, width=300)
        # aruco generator
        self.draw_aruco_generator_frame(self.frame_left)
        # calibration fraem
        self.draw_calibration_frame(self.frame_left)
        self.frame_left.grid(column=0, row=0)
        
        # right frame
        self.frame_right = ttk.Frame(self.frame_container)
        self.frame_right.configure(height=200, width=200)
        self.draw_status_frame(self.frame_right)
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
            text='Yes', textvariable=self.var_is_calibrated)
        self.label_is_detection_ready.grid(column=1, padx=10, row=0)
        frame10.pack(ipadx=10, pady=10, side="top")
        frame14 = ttk.Frame(self.label_frame_detect)
        frame14.configure(height=200, width=200)
        title_label5 = ttk.Label(frame14)
        title_label5.configure(text='Websocket IP:')
        title_label5.grid(column=0, row=0)
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
        pass
        
    def draw_button(self, parent, title, callback):
        button = ttk.Button(parent)
        button.configure(text=title)
        button.pack(ipadx=10, pady=10, side="top")
        button.configure(command = callback)
        pass
    
    def draw_icon_button(self, parent, icon, callback):
        button = ttk.Button(parent)
        button.configure(image=icon)
        button.configure(
            command=callback)
        return button
        
    def draw_aruco_generator_frame(self, parent):
        # aruco generator
        frame_aruco_generator = ttk.Labelframe(parent)
        frame_aruco_generator.configure(
            height=200, text='Aruco Generator', width=200)
        self.var_num_of_markers = tk.StringVar(value='36')
        self.draw_number_field(frame_aruco_generator, self.var_num_of_markers, "Num of markers", '36')
        self.var_aruco_size = tk.StringVar(value='5')
        self.draw_cm_number_field(frame_aruco_generator, self.var_aruco_size, "Marker size", '5')
        self.var_aruco_gap_size = tk.StringVar(value='0.5')
        self.draw_cm_number_field(frame_aruco_generator, self.var_aruco_gap_size, "Gap size", '0.5')
        self.draw_button(frame_aruco_generator, 'Generate aruco markers', self.on_click_generate_aruco)
        frame_aruco_generator.pack(
            expand=False, fill="x", padx=20, pady=5, side="top")
        pass
    
    def draw_charuco_pattern_field(self, parent, rowVar: tk.StringVar, colVar: tk.StringVar, title: str, rowDefault: str, colDefault: str):
        pattern_field = ttk.Frame(parent)
        pattern_field.configure(height=200, width=200)
        field_title = ttk.Label(pattern_field)
        field_title.configure(text=title)
        field_title.grid(column=0, row=0)
        value_field = ttk.Frame(pattern_field)
        value_field.configure(height=200, width=200)
        entry_row = ttk.Entry(value_field)
        entry_row.configure(
            justify="center",
            textvariable=rowVar,
            width=3)
        entry_row.delete("0", "end")
        entry_row.insert("0", rowDefault)
        entry_row.grid(column=0, row=0)
        label_x = ttk.Label(value_field)
        label_x.configure(text='x')
        label_x.grid(column=1, row=0)
        entry_column = ttk.Entry(value_field)
        entry_column.configure(
            justify="center",
            textvariable=colVar,
            width=3)
        entry_column.delete("0", "end")
        entry_column.insert("0", colDefault)
        entry_column.grid(column=2, row=0)
        value_field.grid(column=1, padx=10, row=0)
        pattern_field.pack(pady=10, side="top")
        pass
    
    def draw_refreshable_state_field(self, parent, title, variable, default_value, callback):
        frame = ttk.Frame(parent)
        frame.configure(height=200, width=200)
        title_frame = ttk.Frame(frame)
        title_frame.configure(height=200, width=200)
        title_label = ttk.Label(title_frame)
        title_label.configure(
            compound="center",
            justify="center",
            padding=10,
            text=title)
        title_label.pack()
        title_frame.grid(column=0, row=0)
        value_frame = ttk.Frame(frame)
        value_frame.configure(height=200, width=200)
        value_label = ttk.Label(value_frame)
        value_label.configure(
            text=default_value, textvariable=variable)
        value_label.pack()
        value_frame.grid(column=1, row=0)
        button = self.draw_icon_button(frame, self.img_refresh, callback)
        button.grid(column=2, padx=10, row=0)
        frame.pack(
            expand=True, fill="x", padx=10, pady=0, side="top")
        frame.grid_anchor("center")
        pass
    
    def draw_state_field(self, parent, title, variable, default_value):
        frame = ttk.Frame(parent)
        frame.configure(height=200, width=200)
        title_label = ttk.Label(frame)
        title_label.configure(text=title)
        title_label.grid(column=0, row=0)
        value_label = ttk.Label(frame)
        value_label.configure(text=default_value,
                               textvariable=variable)
        value_label.grid(column=1, padx=10, row=0)
        frame.pack(ipadx=10, side="top")
        pass
    
    def draw_calibration_settings(self, parent):
        frame_board_settings = ttk.Labelframe(parent)
        frame_board_settings.configure(
            height=100, text='CharucoBoard Settings', width=200)
        self.var_board_pattern_row = tk.StringVar(value='5')
        self.var_board_pattern_column = tk.StringVar(value='7')
        self.draw_charuco_pattern_field(
            frame_board_settings, self.var_board_pattern_row, self.var_board_pattern_column, 'Pattern', '5', '7')
        self.draw_button(frame_board_settings, 'Generate charuco board', self.on_click_generate_charuco_board)
        frame_board_settings.pack(
            expand=True, fill="x", padx=20, pady=10, side="top")
        pass
        
    def draw_calibration_frame(self, parent):
        self.img_refresh = tk.PhotoImage(file="assets/refresh.png")
        frame_calibration = ttk.Labelframe(parent)
        frame_calibration.configure(text='Calibration', width=200)
        self.draw_calibration_settings(frame_calibration)
        
        self.var_sample_image_count = tk.StringVar(value='0')
        self.draw_refreshable_state_field(
            frame_calibration, 'Sampled image count:', self.var_sample_image_count, '0', self.on_click_refresh_sampled_count)
        self.draw_button(frame_calibration, 'Capture sample images', self.on_click_capture_sample_images)

        self.draw_button(
            frame_calibration, 'Calibrate camera', self.on_click_calibrate_camera
        )
        frame_calibration.pack(
            expand=False, fill="x", padx=20, pady=5, side="top")
        pass
    
    def draw_status_frame(self, parent):
        frame_status = ttk.Labelframe(parent)
        frame_status.configure(height=200, text='Status', width=200)
        
        self.var_is_calibrated = tk.StringVar(value='No')
        self.var_is_camera_ready = tk.StringVar(value='No')
        
        self.draw_state_field(frame_status, 'Is Calibrated: ', self.var_is_calibrated, 'No')
        self.draw_state_field(frame_status, 'Is Camera ready:', self.var_is_camera_ready, 'No')
        
        button_refresh = self.draw_icon_button(frame_status, self.img_refresh, self.refresh_status)
        button_refresh.pack(ipadx=0, pady=5, side="top")

        frame_status.pack(
            fill="x",
            ipady=10,
            padx=10,
            pady=10,
            side="top")
        
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
        self.update_num_sampled_images()
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
        self.refresh_status()
        pass

    def on_click_detect(self):
        print("Start detecting")
        ip = self.var_websocket_ip.get()
        calibFilePath = f'{pathlib.Path().resolve()}/resources/calib.npz'
        detector.detect_arucos(calibFilePath, ip)
        pass
    
    def update_num_sampled_images():
        pass

    def refresh_status(self):
        pass


if __name__ == "__main__":
    app = VreactableApp()
    app.run()