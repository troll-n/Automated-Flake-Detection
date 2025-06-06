"""
Author: Patrick Kaczmarek
Basic stage testing function.
Ensure the controller is turned on before running this program, and that there are no obstructions to the stage.
Check the controller to ensure that the stage goes to where you expect.
Works as of 5/14
"""

from ctypes import WinDLL, create_string_buffer
import os
import sys

# try to connect to priorSDK (for stage control)
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(FILE_DIR, "..", "..", "x64", "PriorScientificSDK.dll")

if os.path.exists(path):
    SDKPrior = WinDLL(path)
else:
    raise RuntimeError("SDK DLL could not be loaded.")

path = "C:\Program Files\Prior Scientific\Prior Software\Prior.dll"

# try to connect to prior legacy (for stage control)
if os.path.exists(path):
    LegacyPrior = WinDLL(path)
else:
    raise RuntimeError("Legacy DLL could not be loaded.")

rx = create_string_buffer(1000)
realhw = True


def cmd(msg):
    print(msg)
    ret = SDKPrior.PriorScientificSDK_cmd(
        sessionID, create_string_buffer(msg.encode()), rx
    )
    if ret:
        print(f"Api error {ret}")
    else:
        print(f"OK {rx.value.decode()}")

    input("Press ENTER to continue...")
    return ret, rx.value.decode()


ret = SDKPrior.PriorScientificSDK_Initialise()
if ret:
    print(f"Error initialising {ret}")
    sys.exit()
else:
    print(f"Ok initialising {ret}")


ret = SDKPrior.PriorScientificSDK_Version(rx)
print(f"dll version api ret={ret}, version={rx.value.decode()}")


sessionID = SDKPrior.PriorScientificSDK_OpenNewSession()
if sessionID < 0:
    print(f"Error getting sessionID {ret}")
else:
    print(f"SessionID = {sessionID}")


ret = SDKPrior.PriorScientificSDK_cmd(
    sessionID, create_string_buffer(b"dll.apitest 33 goodresponse"), rx
)
print(f"api response {ret}, rx = {rx.value.decode()}")
input("Press ENTER to continue...")


ret = SDKPrior.PriorScientificSDK_cmd(
    sessionID, create_string_buffer(b"dll.apitest -300 stillgoodresponse"), rx
)
print(f"api response {ret}, rx = {rx.value.decode()}")
input("Press ENTER to continue...")



if realhw:
    print("Connecting...")
    cmd("controller.connect 3")
    # substitute 3 with your com port Id
        
    cmd("controller.stage.position.set 0 0")
    cmd("controller.stage.goto-position -25000 -25000")

    cmd("controller.stage.goto-position 1000 1000")
    cmd("controller.stage.goto-position -1000 -1000")
    cmd("controller.stage.goto-position 0 0")


else:
    input("Press ENTER to continue...")

cmd("controller.disconnect")