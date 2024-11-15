# basics
import argparse, json, os, sys
import cv2
import numpy as np
# custom imports
from GMMDetector import MaterialDetector
# stage
import stage_wrapper
# Blackfly camera
from rotpy.system import SpinSystem
from rotpy.camera import CameraList

def chipmap(stage, chip_id, chip_x, chip_y) -> str:
    """
    Map the loaded chip at 4x magnification

    Arguments:
        stage: Our stage object
        chip_id: int, ID of the chip, important for database storage
        chip_x: float, x-dimension of the chip. mm
        chip_y: float, y-dimension of the chip, mm
    Requires:
        0,0 set for stage (done in detect_flakes)
    Ensures:
        Mapped chip is saved in proper location as a jpg - read README.md if confused
    Returns:
        filename: Filename of the mapped chip.
    """
    # Filename we'll use for this chipmap 
    filename = "map_" + str(chip_id) + ".jpg"
    # We'll capture a little bit extra just so we're not leaving anything out; this won't be repeated
    microns_per_capture = 1000 # how many microns per capture; determined experimentally
    # Below in MICRONS (prior microscope does it in microns)
    margin = 500 # extra captured on each side
    cap_x = chip_x * pow(10,3) + 2*margin
    cap_y = chip_y * pow(10,3) + 2*margin
    stage.GoTo(((-margin),margin))
    # where can i store all of these images dawg
    # figure out frequency to take images at 4x?
    # figure out speed to set controller to
    
    return filename