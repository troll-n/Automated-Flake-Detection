""" 
NOTE: DONE WITH OLYMPUS WI 10x LENS 
"""

import argparse
import json
import os
import sys

import cv2
import numpy as np

from Utils.misc_functions import visualise_flakes
from GMMDetector import MaterialDetector

import time

from rotpy.system import SpinSystem
from rotpy.camera import CameraList

from ctypes import WinDLL, create_string_buffer

# constants 
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRAST_PATH_ROOT = os.path.join(FILE_DIR, "..", "..", "..", "GMMDetector", "trained_parameters")
DATA_DIR = os.path.join(FILE_DIR, "..", "Datasets", "GMMDetectorDatasets") 
OUT_DIR = os.path.join(FILE_DIR, "Output") 
IN_DIR = os.path.join(FILE_DIR, "Input") 

rx = create_string_buffer(1000)
sdkpath = os.path.join(FILE_DIR, "..", "..", "x64", "PriorScientificSDK.dll")
if os.path.exists(sdkpath):
    SDKPrior = WinDLL(sdkpath)
else:
    raise RuntimeError("DLL could not be loaded.")
# stage command:passes commands to the controller
def scmd(msg):
    print(msg)
    ret = SDKPrior.PriorScientificSDK_cmd(
        sessionID, create_string_buffer(msg.encode()), rx
    )
    if ret:
        print(f"Api error {ret}")
    else:
        print(f"OK {rx.value.decode()}")

    input("Press ENTER to continue...")
    return ret, rx.value.decode()

def sGoTo(coord):
    
    scmd("controller.stage.goto-position %d %d" % (coord[0], coord[1]))
    return

ret = SDKPrior.PriorScientificSDK_Initialise()
if ret:
    print(f"Error initialising {ret}")
    sys.exit()
else:
    print(f"Ok initialising {ret}")


ret = SDKPrior.PriorScientificSDK_Version(rx)
print(f"dll version api ret={ret}, version={rx.value.decode()}")


sessionID = SDKPrior.PriorScientificSDK_OpenNewSession()
if sessionID < 0:
    print(f"Error getting sessionID {ret}")
else:
    print(f"SessionID = {sessionID}")


ret = SDKPrior.PriorScientificSDK_cmd(
    sessionID, create_string_buffer(b"dll.apitest 33 goodresponse"), rx
)
print(f"api response {ret}, rx = {rx.value.decode()}")
input("Press ENTER to continue...")


MATERIAL = "Graphene"
SIZE_THRESHOLD = 200
STD_THRESHOLD = 5
genname = "stagetest0"

# loads up the contrast dictionary for whatever material we want
with open(os.path.join(CONTRAST_PATH_ROOT, f"Graphene_GMM.json")) as f:
    contrast_dict = json.load(f)

system = SpinSystem()
cameras = CameraList.create_from_system(system, True, True)
camera = cameras.create_camera_by_serial('22580849') # camera serial ###
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

# list of places to send the stage
coords = [(0,0), (2000, 2000), (100,100), (-2000, -2000), (0,0)]

print("Connecting...")
scmd("controller.connect 3")
scmd("controller.stage.position.set 0 0")
# substitute 3 with your com port Id
i = 0
for coord in coords:

    coordstr = "("  +str(coord[0]) + "," + str(coord[1]) + ")"
    imgname = genname + str(i)  + "at" + coordstr + ".jpg"
    sGoTo(coord)
    
    # obtain an image
    camera.begin_acquisition()
    image_cam = camera.get_next_image()
    image = image_cam.deep_copy_image(image_cam)
    image_cam.release()
    camera.end_acquisition()
    # make the image a numpy array
    jpeg_path = os.path.join(IN_DIR, imgname)
    image.save_jpeg(jpeg_path)
    imgnp = cv2.imread(jpeg_path) # need a better system than this

    flakes = model(imgnp)
    print(flakes)
    print("Flake list length: ", flakes.shape)

    # save whatever
    # 
    image_overlay = visualise_flakes(flakes, imgnp, 0.8)
    # saves the image
    cv2.imwrite(os.path.join(OUT_DIR, imgname), image_overlay)
    i = i + 1
scmd("controller.disconnect")

# cleanup
camera.deinit_cam()
camera.release()