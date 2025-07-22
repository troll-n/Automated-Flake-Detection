"""
To run this file, click the play button in the top right.
After doing so, the terminal will have information regarding the z-axis.
You will have to press enter in the terminal to continue - this is so you don't accidently crash the lens into the floor or anything.
Don't forget to turn the controller on!
"""

import argparse
import json
import os
import sys


# stage
from ctypes import WinDLL, create_string_buffer
from stage_wrapper import Stage

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

stage = Stage(FILE_DIR)
stage.debug(True)
stage.setZeros(20)

input("Change magnification to 4x please!\n")
stage.refocus(4)

input("Change magnification to 10x please!\n")
stage.refocus(10)

input("Change magnification to 20x please!\n")
stage.refocus(20)

for x in range(0,10):
    z = int(stage.retCmd("controller.z.position.get"))
    print("current z: %d" % z)
    z = z + 100 * x
    stage.Z_GoTo(z)