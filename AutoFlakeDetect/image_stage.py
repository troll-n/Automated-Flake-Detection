# basics
import argparse, json, os, sys
import cv2
import numpy as np
import time
# custom imports
from GMMDetector import MaterialDetector
# stage
from stage_wrapper import Stage
# Blackfly camera
from rotpy.system import SpinSystem
from rotpy.camera import CameraList

def image_chip(stage, camera, SAVE_DIR, mag, chip_id, chip_x, chip_y):
    """
    Image the loaded chip at Zx magnification

    Arguments:
        stage: Our stage object
        camera: Our SpinSystem Camera object
        SAVE_DIR: Directory to save images to
        mag: Magnification level
        chip_id: int, ID of the chip, important for database storage
        chip_x: float, x-dimension of the chip. mm
        chip_y: float, y-dimension of the chip, mm
    Requires:
        0,0 set for stage (done in detect_flakes), top left
    Ensures:
        Mapped chip is saved in proper location as a jpg - read README.md if confused
    Returns:
        filename: Filename of the mapped chip.
    """
    # defaults (throws error if not changed)

    # General prefix that we'll use for this chip 
    prefix = "ch" + str(chip_id) + "_"
    start = time.time()
    microns_per_x_capture = 0 
    microns_per_y_capture = 0
    if mag == 4:
        #already set
        microns_per_x_capture = 2100 
        microns_per_y_capture = 1700
    elif mag == 10:
        #found experimentally
        microns_per_x_capture = 840 
        microns_per_y_capture = 750
    elif mag == 20:
        microns_per_x_capture = 420 
        microns_per_y_capture = 350
    else:
        #haven't determined it yet, I'll just pretend it's roughly linear
        print("Estimating necessary microns needed per capture (this may be choppy)\n")
        slopex = (840-2100)/6
        slopey = (750-1700)/6
        microns_per_x_capture = int(slopex * mag)
        microns_per_y_capture = int(slopey * mag)

    # Below in MICRONS (prior microscope does it in microns)
    marginx = int(microns_per_x_capture / 2)
    marginy = int(microns_per_y_capture / 2)
    cap_x = int(chip_x * 1000 + (mag / 2) * marginx)
    cap_y = int(chip_y * 1000 + (mag / 2) * marginy)
    count = 0
    for x in range(-marginx, cap_x, microns_per_x_capture):
        for y in range(-marginy, cap_y,microns_per_y_capture):
            count+=1
            busyStatus = int(stage.retCmd( "controller.stage.busy.get"))
            while busyStatus != 0:
                time.sleep(0.15)
                busyStatus = int(stage.retCmd("controller.stage.busy.get"))
            stage.GoTo((-x,-y))
            # obtain an image
            camera.begin_acquisition()
            image_cam = camera.get_next_image()
            image = image_cam.deep_copy_image(image_cam)
            image_cam.release()
            camera.end_acquisition()
            # save it
            imgname = prefix + str(count) + ".jpg"
            jpeg_path = os.path.join(SAVE_DIR, imgname)
            image.save_jpeg(jpeg_path)
            #controller defintely has a limit of some kind, make sure i don't overload it
    print("total images taken: %d", count)
    print("to complete, function took the following amount of seconds:", int(time.time() - start))



def chipmap(stage, mag, chip_id, chip_x, chip_y) -> str:
    """
    Map the loaded chip at magx magnification

    Arguments:
        stage: Our Prior stage object
        camera: Our SpinSystem Camera object
        mag: Magnification level
        chip_id: int, ID of the chip, important for database storage
        chip_x: float, x-dimension of the chip. mm
        chip_y: float, y-dimension of the chip, mm
    Requires:
        0,0 set for stage (done in detect_flakes), top left
    Ensures:
        Mapped chip is saved in proper location as a jpg - read README.md if confused
    Returns:
        filename: Filename of the mapped chip.
    """
    # Filename we'll use for this chipmap 
    filename = "map_" + str(chip_id) + ".jpg"
    # We'll capture a little bit extra just so we're not leaving anything out; this won't be repeated
    image_chip(stage, mag, chip_id, chip_x, chip_y)
    # 
    # figure out frequency to take images at 4x?
    # figure out speed to set controller to
    
    return filename

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(FILE_DIR, "4xtest_images")
system = SpinSystem()
cameras = CameraList.create_from_system(system, True, True)
camera = cameras.create_camera_by_serial('23309234') # camera serial ###
camera.init_cam()
camera.camera_nodes.PixelFormat.set_node_value_from_str('BGR8') #converts better to np array


stage = Stage(FILE_DIR)
stage.debug(False)
# POINT CAMERA AT TOP LEFT OF CHIP BEFORE RUNNING THIS PROGRAM!
# Also note that one cannot run the SpinNaker porgram and this one at the same time.
stage.cmd("controller.stage.position.set 0 0")
image_chip(stage, camera, SAVE_DIR, 4, 0, 9.107, 10.461)

# cleanup
camera.deinit_cam()
camera.release()
stage.cmd("controller.disconnect")