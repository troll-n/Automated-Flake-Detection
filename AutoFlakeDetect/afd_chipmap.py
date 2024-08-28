# basics
import argparse, json, os, sys
import cv2
import numpy as np
# custom imports
from Utils.misc_functions import visualise_flakes
from GMMDetector import MaterialDetector
# stage
from ctypes import WinDLL, create_string_buffer
# Blackfly camera
from rotpy.system import SpinSystem
from rotpy.camera import CameraList

def chipmap(chip_id, ) -> str:
    """
    Map the loaded chip at 4x magnification

    Arguments:
        chip_id: ID of the chip, important for database storage
        chip_x: x-dimension of the chip. mm
        chip_y: y-dimension of the chip, mm
    Outcomes:
        Mapped chip is saved in proper location as a jpg - read README.md if confused
        Filename of image is returned
    Returns:
        filename: Filename of the mapped chip.
    """
    # want to start in top left, zeroed out
    # figure out frequency to take images at 4x?
    # figure out sped to set controller to
    filename = "chipmap" + str(chip_id) + ".jpg"
    return filename