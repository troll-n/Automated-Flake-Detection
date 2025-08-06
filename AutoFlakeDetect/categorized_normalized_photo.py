"""
just a loop for speeding up the taking of images for the detector
"""


import cv2
import time
import os
import json
import numpy as np
from img_utils import normalize_Gr
# Blackfly camera
from rotpy.system import SpinSystem
from rotpy.camera import CameraList

from Utils.misc_functions import visualise_flakes
from GMMDetector import MaterialDetector


system = SpinSystem()
cameras = CameraList.create_from_system(system, True, True)
camera = cameras.create_camera_by_serial('22580849') # camera serial ###
camera.init_cam()
camera.camera_nodes.PixelFormat.set_node_value_from_str('BGR8')

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(FILE_DIR, "..", "Native_Datasets", "Graphene", "data")

backgroundPath = os.path.join(DATA_DIR, "f1558v.jpg")
background = cv2.imread(backgroundPath)

chipname = input("Chip name/ID? ")

count = 0
keepGoing = True
buff = np.full([1920*1200*3],0,np.uint8)

while keepGoing:
    com = input("'x' for escape, anything else to save an image: ")
    if com == "x":
        keepGoing = False
    else:
        imgname = chipname + "_" + str(count) + ".jpg"
        imgpath = os.path.join(DATA_DIR, imgname)
        if os.path.exists(imgpath): 
            camera.deinit_cam()
            camera.release()
            raise Exception("you attempted to save over another image")
        count += 1
        # obtain an image
        camera.begin_acquisition()
        image_cam = camera.get_next_image()
        # transfer data into buffer
        image_cam.copy_image_data(buff)
        #release the camera we don't need it
        image_cam.release()
        camera.end_acquisition()
        # re-organize it into a 3d array (idt the data changes so much as a pointer is thrown in to the address in memory)
        # this is where i wish i was coding in C
        imgnp = np.ndarray([1200,1920,3], buffer=buff, dtype=np.uint8)
        #normalize it
        imgnp = normalize_Gr(imgnp, background)
        cv2.imwrite(imgpath,imgnp)


camera.deinit_cam()
camera.release()