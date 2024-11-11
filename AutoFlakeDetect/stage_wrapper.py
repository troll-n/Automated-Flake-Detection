"""
Authored by Patrick Kaczmarek
Library that wraps the stage commands up as an object
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
        input("Press ENTER to continue...")

    # stage command: passes commands to the controller
    def cmd(self, msg):
        print(msg)
        ret = self.SDKPrior.PriorScientificSDK_cmd(
            self.sessionID, create_string_buffer(msg.encode()), self.rx
        )
        if ret:
            print(f"Api error {ret}")
        else:
            print(f"OK {self.rx.value.decode()}")

        input("Press ENTER to continue...")
        return ret, self.rx.value.decode()