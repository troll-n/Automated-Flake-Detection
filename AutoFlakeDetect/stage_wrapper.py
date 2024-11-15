"""
Authored by Patrick Kaczmarek\n
Library that wraps the stage commands up as an object\n
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np
from ctypes import WinDLL, create_string_buffer

class Stage:
    sdkpath = ""
    SDKPrior = ""
    rx = 0
    sessionID = ""
    debug = False

    def __init__(self, FILE_DIR):
        self.sdkpath = os.path.join(FILE_DIR, "..", "PriorSDK", "x64", "PriorScientificSDK.dll")
        self.rx = create_string_buffer(1000)
        if os.path.exists(self.sdkpath):
            self.SDKPrior = WinDLL(self.sdkpath)
        else:
            raise RuntimeError("DLL could not be loaded.")

        ret = self.SDKPrior.PriorScientificSDK_Initialise()
        if ret:
            print(f"Error initialising {ret}")
            sys.exit()
        else:
            print(f"Ok initialising {ret}")


        ret = self.SDKPrior.PriorScientificSDK_Version(self.rx)
        print(f"dll version api ret={ret}, version={self.rx.value.decode()}")


        self.sessionID = self.SDKPrior.PriorScientificSDK_OpenNewSession()
        if self.sessionID < 0:
            print(f"Error getting sessionID {ret}")
        else:
            print(f"SessionID = {self.sessionID}")


        ret = self.SDKPrior.PriorScientificSDK_cmd(
            self.sessionID, create_string_buffer(b"dll.apitest 33 goodresponse"), self.rx
        )
        print(f"api response {ret}, rx = {self.rx.value.decode()}")
        if self.debug: input("Press ENTER to continue...")

    # stage command: passes any commands to the controller
    def cmd(self, msg) -> tuple:
        print(msg)
        ret = self.SDKPrior.PriorScientificSDK_cmd(
            self.sessionID, create_string_buffer(msg.encode()), self.rx
        )
        if ret:
            print(f"Api error {ret}")
        else:
            print(f"OK {self.rx.value.decode()}")

        if self.debug: input("Press ENTER to continue...")
        return ret, self.rx.value.decode()
    
    # stage command but for if you expect a return value
    def retCmd(self, msg):
        print(msg)
        ret = self.SDKPrior.PriorScientificSDK_cmd(
            self.sessionID, create_string_buffer(msg.encode()), self.rx
        )
        return self.rx.value.decode()
      
    # wrapper function for movement to make loops legible elsewhere
    def GoTo(self, coord) -> tuple:
        return self.cmd("controller.stage.goto-position %d %d" % (coord[0], coord[1]))
    # ditto but for focusing with z axis
    def Z_GoTo(self, coord) -> tuple:
        return self.cmd("controller.z.goto-position %d" % (coord))
    # Set the value of debug; by default false
    def debug(self, val):
        self.debug = val
