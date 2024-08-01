import argparse
import json
import os

import cv2
import numpy as np

from demo.demo_functions import visualise_flakes
from GMMDetector import MaterialDetector

import time

from rotpy.system import SpinSystem
from rotpy.camera import CameraList

# constants 
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRAST_PATH_ROOT = os.path.join(FILE_DIR, "..", "GMMDetector", "trained_parameters")
DATA_DIR = os.path.join(FILE_DIR, "..", "Datasets", "GMMDetectorDatasets") 
OUT_DIR = os.path.join(FILE_DIR, "Output") 
IN_DIR = os.path.join(FILE_DIR, "Input") 

MATERIAL = "Graphene"
SIZE_THRESHOLD = 200
STD_THRESHOLD = 5

# loads up the contrast dictionary for whatever material we want
with open(os.path.join(CONTRAST_PATH_ROOT, f"{MATERIAL}_GMM.json")) as f:
    contrast_dict = json.load(f)

system = SpinSystem()
cameras = CameraList.create_from_system(system, True, True)
camera = cameras.create_camera_by_serial('23309234') # camera serial ###
camera.init_cam()
camera.camera_nodes.PixelFormat.set_node_value_from_str('BGR8') #converts better to np array

# makes a model object
model = MaterialDetector(
    # passes constrast_dict that we made above
    contrast_dict=contrast_dict,
    # size threshold in pixels, 200 nm
    size_threshold=SIZE_THRESHOLD,
    standard_deviation_threshold=STD_THRESHOLD,
    used_channels="BGR",
)



# obtain an image
camera.begin_acquisition()
image_cam = camera.get_next_image()
image = image_cam.deep_copy_image(image_cam)
image_cam.release()
camera.end_acquisition()


# make the image a numpy array
jpeg_path = os.path.join(IN_DIR, 'huh.jpg')
image.save_jpeg(jpeg_path)
imgnp = cv2.imread(jpeg_path)

flakes = model(image)
print(flakes)

# save whatever
# 
image_overlay = visualise_flakes(flakes, image, 0.5)
# saves the image
cv2.imwrite(os.path.join(OUT_DIR, "huh.jpg"), image_overlay)

# cleanup
camera.deinit_cam()
camera.release()




