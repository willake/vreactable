import pathlib
import tkinter.ttk as ttk
from tkinter.messagebox import showerror, showwarning, showinfo
import pygubu
import camera_calibrator.sample_image_capturer as sample_image_capturer
import cv2.aruco as aruco
from detector import detector
from aruco_generators import generator
from helper import helper
import pathlib
import os
import sys
import configparser
config = configparser.ConfigParser()
config.read('./config.ini')

MARKER_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['MarkerFolder'])
PACKED_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['PackedFolder'])
CHARUCO_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['CharucoFolder'])
SAMPLE_FOLDER = os.path.join(helper.getRootPath(), config['PATH']['SampleFolder'])

ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)

# PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_PATH = '.'
PROJECT_UI = f"{PROJECT_PATH}/vreactable.ui"
# PROJECT_UI = PROJECT_PATH / "vreactable.ui"


class VreactableApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow = builder.get_object("toplevel_vreactable", master)

        self.var_aruco_dict = None
        self.var_num_of_markers = None
        self.var_aruco_size = None
        self.var_aruco_gap_size = None
        self.var_board_pattern_row = None
        self.var_board_pattern_column = None
        self.var_sample_image_count = None
        self.var_is_calibrated = None
        builder.import_variables(self,
                                 ['var_aruco_dict',
                                  'var_num_of_markers',
                                  'var_aruco_size',
                                  'var_aruco_gap_size',
                                  'var_board_pattern_row',
                                  'var_board_pattern_column',
                                  'var_sample_image_count',
                                  'var_is_calibrated'])
        
        # combobox
        # combo = self.builder.get_object("combobox_dict")
        # combo['values'] = ('value1', 'value2', 'value3')
        # combo.current(0)
        
        builder.connect_callbacks(self)
        
        numImgs = helper.count_images(SAMPLE_FOLDER)
        self.var_sample_image_count.set(str(numImgs))

    def run(self):
        self.mainwindow.mainloop()

    def on_select_dictionary(self):
        pass

    def on_type_num_of_markers(self):
        pass

    def on_type_aruco_size(self, p_entry_value):
        pass

    def on_type_pattern(self):
        pass
    
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
        generator.generateCharucoBoard(outputFolder = CHARUCO_FOLDER, arucoDict = ARUCO_DICT, pattern = pattern)
        showinfo(title = 'Generate Aruco Markers', message = f'Successfully generated aruco markers. \n The files are at: {CHARUCO_FOLDER}')
        pass
    
    def on_click_refresh_sampled_count(self):
        numImgs = helper.count_images(SAMPLE_FOLDER)
        self.var_sample_image_count.set(str(numImgs))
        pass

    def on_click_capture_sample_images(self):
        sample_image_capturer.capture_sample_images(SAMPLE_FOLDER)

    def on_click_calibrate_camera(self):
        pass

    def on_click_detect(self):
        print("Start detecting")
        calibFilePath = f'{pathlib.Path().resolve()}/resources/calib.npz'
        detector.detect_arucos(calibFilePath)


if __name__ == "__main__":
    app = VreactableApp()
    app.run()
