"""
Author: Patrick Kaczmarek
Basic loader testing function.
Ensure the controller is turned on before running this program, and that there are no obstructions to the stage.
Check the loader visually to ensure that the loader goes to where you expect.
"""

import ctypes as ct
import os
import sys

loaderPort = ct.c_long(5)
controlPort = ct.c_long(3)

path = "C:\Program Files\Prior Scientific\Prior Software\Prior.dll"
# try to connect to prior legacy (for stage control)
if os.path.exists(path):
    LegacyPrior = ct.WinDLL(path)
else:
    raise RuntimeError("Legacy DLL could not be loaded.")

loader = LegacyPrior.SlideLoader()

LegacyPrior.SlideLoader.Connect(ct.byref(controlPort))

if controlPort < 0:
    raise RuntimeError("Unable to connect to controller, error code ", controlPort)


LegacyPrior.SlideLoader.DisConnect()
