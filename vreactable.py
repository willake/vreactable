#!/usr/bin/python3
import pathlib
import tkinter.ttk as ttk
import pygubu
import camera_calibrator.sample_image_capturer as sample_image_capturer
from detector import detector
import pathlib
import os
import sys
PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "vreactable.ui"


class VreactableApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow = builder.get_object("toplevel_vreactable", master)

        self.sample_image_count = None
        self.is_calibrated = None
        builder.import_variables(self, ['sample_image_count', 'is_calibrated'])

        builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def on_type_pattern(self):
        pass

    def on_click_capture_sample_images(self):
        print("Start capturing")
        sample_image_capturer.capture_sample_images()

    def on_click_calibrate_camera(self):
        pass

    def on_click_detect(self):
        print("Start detecting")
        calibFilePath = f'{pathlib.Path().resolve()}/resources/calib.npz'
        detector.detect_arucos(calibFilePath)


if __name__ == "__main__":
    app = VreactableApp()
    app.run()
