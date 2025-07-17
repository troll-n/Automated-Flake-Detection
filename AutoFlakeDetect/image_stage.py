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

def rect_map_chip(stage, camera, SAVE_DIR, mag, chip_id, chip_x, chip_y):
    """
    Images the loaded chip with a rectangular strip-based algorithm; DOES make a map image 
    Primarily legacy due to the existence of map_chip; that one's more efficient. Use it!

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

    # Fetching the parameters necessary for imaging; see function for more details
    (microns_per_x_capture,microns_per_y_capture,
     micron_x_shift_per_col,micron_y_shift_per_row) = fetch_parameters(mag)
    
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
    
    if(len(xToVisit) * len(yToVisit) > 200):
        print("""Warning: You are about to make a very massive image, perhaps due to having a unnecessarily high magnification setting or loading a particularly large chip. \n
              This program will take a long time to complete, and even if it does, the finished map image may fail to be saved due to limitations in the library this program uses.\n
              """)
        if (input("Enter N to exit program, or anything else to continue anyways: ") == "N"):
            assert(False)

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

            stage.GoTo((-(x+micron_x_shift_per_col*yCount),-(y+micron_y_shift_per_row*xCount)))

            while busyStatus != 0:
                time.sleep(0.05)
                busyStatus = int(stage.retCmd("controller.stage.busy.get"))
            # wait so that stuff looks good; this part to be removed once snake algo is finished
            if yCount == 0:
                time.sleep(0.75)
            else:
                time.sleep(0.25)

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

def map_chip(stage, camera, SAVE_DIR, mag, chip_id, chip_x, chip_y):
    """
    Images the loaded chip with a snaking strip-based algorithm; DOES make a map image 

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

    # Fetching the parameters necessary for imaging; see function for more details
    (microns_per_x_capture,microns_per_y_capture,
     micron_x_shift_per_col,micron_y_shift_per_row) = fetch_parameters(mag)
    
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
    
    if(len(xToVisit) * len(yToVisit) > 200):
        print("""Warning: You are about to make a very massive image, perhaps due to having a unnecessarily high magnification setting or loading a particularly large chip. \n
              This program will take a long time to complete, and even if it does, the finished map image may fail to be saved due to limitations in the library this program uses.\n
              """)
        if (input("Enter N to exit program, or anything else to continue anyways: ") == "N"):
            assert(False)

    img_map = 0

    for x in xToVisit:
        # make a new stripe that lives in this scope
        img_stripe = 0
        adapted_yToVisit = 0
        if xCount % 2 == 0:
            adapted_yToVisit = yToVisit
            yCount = 0
        else:
            adapted_yToVisit = reversed(yToVisit)
            yCount = len(yToVisit) - 1
        is_x_Even = (xCount % 2 == 0)
        is_y_Start = True
        for y in adapted_yToVisit:
            
            count+=1 #can't believe ++ isn't a thing in python

            # move to next place desired to image
            busyStatus = int(stage.retCmd( "controller.stage.busy.get"))
            while busyStatus != 0:
                time.sleep(0.05)
                busyStatus = int(stage.retCmd("controller.stage.busy.get"))

            stage.GoTo((-(x+micron_x_shift_per_col*yCount),-(y+micron_y_shift_per_row*xCount)))

            while busyStatus != 0:
                time.sleep(0.05)
                busyStatus = int(stage.retCmd("controller.stage.busy.get"))
            # wait for a little
            
            if (is_y_Start):
                # wait longer because side to side movement takes longer than up and down
                time.sleep(0.25)
            else:
                time.sleep(0.2)
            
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
            with Image.open(jpeg_path) as im:
                # add to current downstripe if not the first
                if is_y_Start:
                    img_stripe = im.copy()
                    is_y_Start = False
                else:
                    if (is_x_Even):
                        img_stripe = mg.imgDown(img_stripe,im)
                    else:
                        # reverse of down is up, so just flip the arguments
                        img_stripe = mg.imgDown(im,img_stripe)
            # change y-iterator the right way 
            if (is_x_Even):
                yCount+=1
            else:
                yCount-=1
        # we have completed a stripe, add it to the map
        # does not matter wheter xCount is even or odd here
        if xCount == 0:
            #this is our first stripe; we need to make our map a copy of it
            img_map = img_stripe.copy()
        else: 
            # merge this stripe with our overall map
            img_map = mg.imgRight(img_map,img_stripe)
        xCount+=1
    
    #don't forget to save the map!
    img_map.save(mappath)
    print("total images taken:", count)
    print("to complete, function took the following amount of seconds:", int(time.time() - start))

    #return to where we started off because that's nice
    stage.GoTo((0,0))
    return (len(xToVisit),len(yToVisit))

def scan_chip(stage, camera, SAVE_DIR, chip_id, chip_x, chip_y):
    """
    Scans the loaded chip with a snaking algorithm. Magnification is always 20x

    Arguments:
        stage: Our stage object
        camera: Our SpinSystem Camera object
        SAVE_DIR: Directory to save images to
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
    mag = 20

    # Fetching the parameters necessary for imaging; see function for more details
    (microns_per_x_capture,microns_per_y_capture,
     micron_x_shift_per_col,micron_y_shift_per_row) = fetch_parameters(mag)
    
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
    
    if(len(xToVisit) * len(yToVisit) > 200):
        print("""Warning: You are about to make a very massive image, perhaps due to having a unnecessarily high magnification setting or loading a particularly large chip. \n
              This program will take a long time to complete, and even if it does, the finished map image may fail to be saved due to limitations in the library this program uses.\n
              """)
        if (input("Enter N to exit program, or anything else to continue anyways: ") == "N"):
            assert(False)

    img_map = 0

    for x in xToVisit:
        # make a new stripe that lives in this scope
        img_stripe = 0
        adapted_yToVisit = 0
        if xCount % 2 == 0:
            adapted_yToVisit = yToVisit
            yCount = 0
        else:
            adapted_yToVisit = reversed(yToVisit)
            yCount = len(yToVisit) - 1
        is_x_Even = (xCount % 2 == 0)
        is_y_Start = True
        for y in adapted_yToVisit:
            
            count+=1 #can't believe ++ isn't a thing in python

            # move to next place desired to image
            busyStatus = int(stage.retCmd( "controller.stage.busy.get"))
            while busyStatus != 0:
                time.sleep(0.05)
                busyStatus = int(stage.retCmd("controller.stage.busy.get"))

            stage.GoTo((-(x+micron_x_shift_per_col*yCount),-(y+micron_y_shift_per_row*xCount)))

            while busyStatus != 0:
                time.sleep(0.05)
                busyStatus = int(stage.retCmd("controller.stage.busy.get"))
            # wait for a little
            
            if (is_y_Start):
                # wait longer because side to side movement takes longer than up and down
                time.sleep(0.25)
            else:
                time.sleep(0.2)
            
            # obtain an image
            camera.begin_acquisition()
            image_cam = camera.get_next_image()
            curr_image = image_cam.deep_copy_image(image_cam)
            image_cam.release()
            camera.end_acquisition()

            # save it
            imgname = prefix + str(xCount) + "_" + str(yCount) + ".jpg"
            jpeg_path = os.path.join(SAVE_DIR, imgname)
            curr_image.save_jpeg(jpeg_path)
            
            # open the image as a PIL image; i know it's silly but rotpy has bad documentation and i can't figure out how to directly convert it in memory
            with Image.open(jpeg_path) as im:
                # look for flakes
                pass
            # change y-iterator the right way 
            if (is_x_Even):
                yCount+=1
            else:
                yCount-=1
        xCount+=1
    
    #don't forget to save the map!
    img_map.save(mappath)
    print("total images taken:", count)
    print("to complete, function took the following amount of seconds:", int(time.time() - start))

    #return to where we started off because that's nice
    stage.GoTo((0,0))
    return (len(xToVisit),len(yToVisit))



def fetch_parameters(mag) -> tuple[int,int,int,int]:
    """
    Given mgnification level, outputs parameters needed for imaging
    Arguments:
        mag: Magnitude objective loaded
    Returns:
        (microns_per_x_capture, microns_per_y_capture, micron_x_shift_per_col, micron_y_shift_per_row), where:

        microns_per_x_capture: How many microns in x to move per capture
        microns_per_y_capture: How many microns in y to move per capture
        micron_x_shift_per_col: How many microns to shift in x per col; necesitated by backlash
        micron_y_shift_per_row: How many microns to shift in y per row; necesitated by backlash
    """    
    # How many microns to move per capture (rectangular)
    microns_per_x_capture = 0 
    microns_per_y_capture = 0
    
    # How many microns to shift per row or column (maps rectangular to parallelagram)
    # Necessary due to backlash
    micron_x_shift_per_col = 0
    micron_y_shift_per_row = 0
    # All of these should be double checked given the dumbassery that's been going on with the stage.
    if mag == 4:
        # optimized
        microns_per_x_capture = 1650 # original 2100
        microns_per_y_capture = 1028 # original 1767
        micron_x_shift_per_col = 24 # original -42
        micron_y_shift_per_row = -40 # original 42
    elif mag == 10:
        # not optimized
        microns_per_x_capture = 663
        microns_per_y_capture = 418
        micron_x_shift_per_col = 10
        micron_y_shift_per_row = -16
    elif mag == 20:
        # optimized
        microns_per_x_capture = 328 
        microns_per_y_capture = 210 
        micron_x_shift_per_col = 5
        micron_y_shift_per_row = -8
    else:
        #haven't determined it yet, I'll just pretend it's roughly linear
        print("Estimating necessary microns needed per capture (this may be choppy)\n")
        slopex = (840-2100)/6
        slopey = (750-1750)/6
        microns_per_x_capture = int(slopex * mag)
        microns_per_y_capture = int(slopey * mag)
    return (microns_per_x_capture, microns_per_y_capture, micron_x_shift_per_col, micron_y_shift_per_row)

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
#input("Change magnification to 4x please!\n")
#stage.setZeros(4)
#stage.refocus(4)
#map_chip(stage, camera, SAVE_DIR, 4, 0, 10, 10)

#input("Change magnification to 10x please!\n")
#stage.refocus(10)
#stage.cmd("controller.stage.position.set 0 0")
SAVE_DIR = os.path.join(FILE_DIR, "10xtest_images")
map_chip(stage,camera,SAVE_DIR,10,0,1,1)

#input("Change magnification to 20x please!\n")
#stage.refocus(20)
#SAVE_DIR = os.path.join(FILE_DIR, "20xtest_images")
#map_chip(stage,camera,SAVE_DIR,20,0,1,1)
# cleanup
camera.deinit_cam()
camera.release()
stage.cmd("controller.disconnect")