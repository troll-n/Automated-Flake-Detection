# basics
import argparse, json, os, sys
import cv2
import numpy as np
import time
from PIL import Image
# custom imports
from GMMDetector import MaterialDetector
import img_merge as mg
# stage
from stage_wrapper import Stage
# Blackfly camera
from rotpy.system import SpinSystem
from rotpy.camera import CameraList

def image_chip(stage, camera, SAVE_DIR, mag, chip_id, chip_x, chip_y):
    """
    Image the loaded chip; does not make a map image.

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
        (cap_x,cap_y)
    """
    # To do:
    # Incorporate autofocus or psuedo-autofocus
    # Make faster (and stabler) by going down-right-up-right instead of down-up-right-down-up
        # Or maybe spiral?
    # Clean up comments (like that's ever gonna happen)
    
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
    # x coords to visit
    xToVisit = range(-marginx, cap_x, microns_per_x_capture)
    # y coords to visit
    yToVisit = range(-marginy, cap_y,microns_per_y_capture)
    for x in xToVisit:
        for y in yToVisit:
            count+=1 #can't believe ++ isn't a thing in python
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
    print("total images taken:", count)
    print("to complete, function took the following amount of seconds:", int(time.time() - start))
    return (len(xToVisit),len(yToVisit))

def map_chip(stage, camera, SAVE_DIR, mag, chip_id, chip_x, chip_y):
    """
    Images the loaded chip; DOES make a map image 

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
        (cap_x,cap_y)
    """

    # defaults (throws error if not changed)

    # General prefix that we'll use for this chip 
    # Filename we'll use for this chip map 
    filename = "map_" + str(chip_id) + ".jpg"
    mappath = os.path.join(SAVE_DIR, filename)
    
    prefix = "ch" + str(chip_id) + "_"
    start = time.time()
    microns_per_x_capture = 0 
    microns_per_y_capture = 0
    if mag == 4:
        #already set
        microns_per_x_capture = 2100 #original: 2100
        microns_per_y_capture = 1750 #original: 1700
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
    # x coords to visit
    xToVisit = range(-marginx, cap_x, microns_per_x_capture)
    xCount = 0
    # y coords to visit
    yToVisit = range(-marginy, cap_y,microns_per_y_capture)
    yCount = 0
    
    img_map = 0

    for x in xToVisit:
        # make a new stripe that lives in this scope
        img_stripe = 0
        for y in yToVisit:
            count+=1 #can't believe ++ isn't a thing in python

            #move to next place desired to image
            busyStatus = int(stage.retCmd( "controller.stage.busy.get"))
            while busyStatus != 0:
                time.sleep(0.05)
                busyStatus = int(stage.retCmd("controller.stage.busy.get"))
            stage.GoTo((-x,-y))
            while busyStatus != 0:
                time.sleep(0.05)
                busyStatus = int(stage.retCmd("controller.stage.busy.get"))
            # wait so that stuff looks good
            time.sleep(0.5)

            # obtain an image
            camera.begin_acquisition()
            image_cam = camera.get_next_image()
            curr_image = image_cam.deep_copy_image(image_cam)
            image_cam.release()
            camera.end_acquisition()
            # save it
            imgname = prefix + str(count) + ".jpg"
            jpeg_path = os.path.join(SAVE_DIR, imgname)
            curr_image.save_jpeg(jpeg_path)
            # open the image as a PIL image; i know it's silly but rotpy has bad documentation and i can't figure out how to directly convert it in memory
            print(yCount)
            with Image.open(jpeg_path) as im:
                # add to current downstripe if not the first
                if yCount == 0:
                    img_stripe = im.copy()
                    print("copied im over")
                else:
                    img_stripe = mg.imgDown(img_stripe,im)
                    print("merged im")
            yCount+=1
        # we have completed a stripe, add it to the map
        if xCount == 0:
            #this is our first stripe; we need to make our map a copy of it
            img_map = img_stripe.copy()
        else: 
            # merge this stripe with our overall map
            img_map = mg.imgRight(img_map,img_stripe)
        yCount = 0
        xCount+=1
    
    #don't forget to save the map!
    img_map.save(mappath)
    print("total images taken:", count)
    print("to complete, function took the following amount of seconds:", int(time.time() - start))

    #return to where we started off because that's nice
    stage.GoTo((0,0))
    return (len(xToVisit),len(yToVisit))




def chipmap(stage, camera, SAVE_DIR, mag, chip_id, chip_x, chip_y) -> str:
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
    # Filename we'll use for this chip map 
    filename = "map_" + str(chip_id) + ".jpg"
    mappath = os.path.join(SAVE_DIR, filename)
    # First, image the chip and put it into a temporary directory, get dims (img#ximg#)
    dims = image_chip(stage, camera, SAVE_DIR, mag, chip_id, chip_x, chip_y)
    # We have now imaged all of the chip, and need to merge ts
    prefix = "ch" + str(chip_id) + "_"
    # Merging time!
    # actual img id. starts at 1 because need to set up
    count = 1
    # count of stripes down; basically all images of the same y-coord
    count_downstripes = -1
    while count_downstripes < dims[0]:
        if (count+1) % dims[1]  == 0:  # special case for if it's the first image to get merged
            #we're done with the old stripe, make a new stripe
            #copy topmost image

            count_downstripes+=1
            mg.imgDown()
        else: 
            pass
        count+=1
    # figure out frequency to take images at 4x?
    # figure out speed to set controller to
    
    return filename

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(FILE_DIR, "4xtest_images")
system = SpinSystem()
cameras = CameraList.create_from_system(system, True, True)
camera = cameras.create_camera_by_serial('22580849') # camera serial ###
camera.init_cam()
camera.camera_nodes.PixelFormat.set_node_value_from_str('BGR8') #converts better to np array


stage = Stage(FILE_DIR)
stage.debug(False)
# POINT CAMERA AT TOP LEFT OF CHIP BEFORE RUNNING THIS PROGRAM!
# Also note that one cannot run the SpinNaker porgram and this one at the same time.
# stage.cmd("controller.stage.position.set 0 0")
map_chip(stage, camera, SAVE_DIR, 4, 0, 13, 13)
# cleanup
camera.deinit_cam()
camera.release()
stage.cmd("controller.disconnect")