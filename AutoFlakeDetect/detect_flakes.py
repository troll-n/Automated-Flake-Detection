"""
Authored by Patrick Kaczmarek
Code that automates flake detection via microscope.
This program should always be run in the 2DMatGMM venv, and expects you to have navigated the microscope to the top left corner of the chip.
Please read GETTING_STARTED.md if you want to use this program.
"""

import argparse
import json
import os
import sys

import cv2
import numpy as np

# ML model
from Utils.misc_functions import visualise_flakes
from GMMDetector import MaterialDetector

# stage
from ctypes import WinDLL, create_string_buffer
from stage_wrapper import Stage

# database
from mysql.connector import Error, connect
from getpass import getpass
from AutoFlakeDetect.image_stage import chipmap

# Blackfly camera
from rotpy.system import SpinSystem
from rotpy.camera import CameraList

# Misc functions
import img_merge as merge

# Strictly necessary functions
def arg_parse() -> dict:
    """
    Parse arguments

    Returns:
        dict: Dictionary of arguments
    """
    # fmt: off
    # arg for size of chips?
    parser = argparse.ArgumentParser(description="2DMatGMM Demo")
    parser.add_argument("--material", dest="material", help="Material to process", default="Graphene", type=str)
    parser.add_argument("--size", dest="size", help="Size threshold in pixels", default=200, type=int)
    parser.add_argument("--min_confidence", dest="min_confidence", help="The Confidence threshold", default=0.5, type=float)
    parser.add_argument("--chip_x", dest="chip_x", help="Chip's size wrt the x-axis, mm", default = 10, type = float)
    parser.add_argument("--chip_y", dest="chip_y", help="Chip's size wrt the y-axis, mm", default = 10, type = float )
    # fmt: on
    return vars(parser.parse_args())

# Some constants
args = arg_parse()

FILE_DIR = os.path.dirname(os.path.abspath(__file__))




# def getTopLeftXY() -> tuple:
#     """
#     Gets the coordinates of the top left of whatever section of the chip the camera is looking at

#     Returns:
#         tuple: Tuple of the x,y coordinate of the top left pixel of the section, relative to global top left.
#     """
#     # getpos with sdk
#     # 
#     pass

# def getFlakeCenterXY(flake) -> tuple:
#     """
#     Gets the coordinates of a flake of interest.

#     Returns:
#         tuple: Tuple of the x,y coordinate of the center pixel of the flake, relative to global top left.
#     """
#     TL_XY = getTopLeftXY()
#     # below is Flake class's native center attrb, measured in pixels, at 20x mag
#     local_center = flake["center"]
    
#     # insert conversion from pixels to whatever the x,y units are
#     return (TL_XY[0] + 0, TL_XY[1] + 0) 




# Constants
CONTRAST_PATH_ROOT = os.path.join(FILE_DIR, "..", "GMMDetector", "trained_parameters") # keep
DATA_DIR = os.path.join(FILE_DIR, "..", "Datasets", "GMMDetectorDatasets") # redirect
OUT_DIR = os.path.join(FILE_DIR, args["out"]) # keep? may want to make unique for every go
# path for camera input
# path for 
os.makedirs(OUT_DIR, exist_ok=True)

MATERIAL = args["material"]
SIZE_THRESHOLD = args["size"]

# PREP PHASE

# Initializing stage - see stage_wrapper.py for more info

stage = Stage(FILE_DIR)
stage.debug(True)

# Initializing camera
system = SpinSystem()
cameras = CameraList.create_from_system(system, True, True)
camera = cameras.create_camera_by_serial('23309234') # camera serial ###
camera.init_cam()
camera.camera_nodes.PixelFormat.set_node_value_from_str('BGR8') #converts better to np array 

# Initializing GMM model

# loads up the contrast dictionary for whatever material we want
with open(os.path.join(CONTRAST_PATH_ROOT, f"{MATERIAL}_GMM.json")) as f:
    contrast_dict = json.load(f)

# makes a model object
model = MaterialDetector(
    # passes constrast_dict that we made above
    contrast_dict = contrast_dict,
    # size threshold in pixels, 200 nm
    size_threshold = SIZE_THRESHOLD,
    # just leave std as 5
    standard_deviation_threshold = 5,
    used_channels="BGR",
)

# Entering new chip into db - currently ints, but I can change to strings if preferred
c_id = 0
try:
    with connect(
        host="localhost",
        user=input("Enter username: "),
        password=getpass("Enter password: "),
        database = "2dmat_db",
    ) as connection:
        # defining querys now so we don't have to later
        insert_chip_query = """
        INSERT INTO chips (material, size)
        VALUES 
            (%s,%d)
        """(args["material"], args["size"])
        get_chip_id_query = """
        SELECT chip_id FROM chips
            ORDER BY chip_id desc
            LIMIT 1
        """
        with connection.cursor() as cursor:
            cursor.execute(insert_chip_query)
            cursor.commit()
            cursor.execute(get_chip_id_query)
            c_id = cursor.fetchall()[0][0]
except Error as e:
    print(e)

# create proper-looking file directory in the same directory as this file; see DB notes below

CHIP_DIR = os.path.join(FILE_DIR, str(c_id))
os.makedirs(CHIP_DIR)

# store flake objects in here; some info will be dumped due to the flake schema of the db + relevance to user
flakes = []
# store x n y info in here; well-ordered list so index of above and below line up
# the choice to do this rather than update the flake class is due to the fact that i don't want to mess with the internals of the classes that the model might be looking at.
flakeXYList = []

# assumes wherever we're at is top left of our chip
stage.cmd("controller.stage.position.set 0 0")
# may also need to figure out how to move the stage properly
# set mag level to 2.5x
# warm up model (?)

# SCANNING PHASE

# Start by scanning the chip at a low magnification level
# Result: Stitched together image - may be sloppy but that's alright, prepped for next phase

# go to top left
# take photo, store somewhere
# move to next area
# repeat
# if all the way to right or left, go one down in y and then swap directions in x
# when done, stitch together all the images and turnit back into a user-accesible image

# Scans at 20x mag level, scan for flakes
# Result: List of flakes, a way to retrieve their x&ys, prepped for next phase

# adj mag level, reset to wherever it's supposed to be 
# may have to adjust model inputs? idk tho

# go to top left

# take photo, pass to model
# note that this photo is not saved anywhere just yet
img_path = "" # fill in from camera here
image = cv2.imread(img_path)
flakesOnImg = model(image)

# awesome, now are there flakes in this image? if so, we're gonna take info about them and
# put it in the proper list 
if flakesOnImg.size > 0:
    for flake in flakesOnImg:
        flakeXYList.append(getFlakeCenterXY(flake))
        flakes.append(flake)

# move to next area
# repeat
# if all the way to right or left, go one down in yand then swap directions in x


# Revisit flakes and take images at different magnification levels
# Result: Images that detail where exactly the flake is

# now, we have a list of where each flake is as well as the flake object proper

# first make all the directories necessary

for i,flake in enumerate(flakes):
    FLAKE_ID = str(i)
    os.makedirs(os.path.join(CHIP_DIR,FLAKE_ID))

# now for the actual scan 
for flake,coord in zip(flakes, flakeXYList):
    # goto x,y of flake
    # take image at 2.5x
    # take image at 20x
    # take image at 50x
    # store images

    pass

# DATABASE PHASE

# assume flakes has been filled out and 2dmat_db is set up
# we first need to organize flakes array so that it's readable by executemany
# while doing this we'll also make dirs for each flake
dbReadyFlakes = []
f_id = 0
# note that flakes list and flakeXYList are well-ordered so their indexes line up, so we can use f_id - 1 to fish out the right one
for flake, coord in zip(flakes,flakeXYList):
    conf = 1 - flake["false_positive_probability"]
    dbReadyFlakes.append(
        (
            c_id, f_id, flake["thickness"], flake["size"], coord[0], coord[1], conf, lowM,medM,highM
        )
        # above appends (chip id, flake id, flake thickness, flake size, flake x coord, flake y coord, 
        # flake confidence, lowmag filepath, medmag filepath, highmag filepath)
    )

    f_id = f_id + 1

try:
    with connect(
        host="localhost",
        user=input("Enter username: "),
        password=getpass("Enter password: "),
        database = "2dmat_db",
    ) as connection:
        # defining querys now so we don't have to later
        insert_flake_query = """
        INSERT INTO flakes (chip_id, flake_id, thickness, size, center_x, center_y, confidence, low_mag, med_mag, high_mag)
        VALUES 
            (%s,%s,%s, %d, %d, %d, %f, %s, %s, %s)
        """
        
        # we made chip at the start so we can just throw our flakes in now
        with connection.cursor() as cursor:
            cursor.executemany(insert_flake_query, dbReadyFlakes)
except Error as e:
    print(e)

# UI?