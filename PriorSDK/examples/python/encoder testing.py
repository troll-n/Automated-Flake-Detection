from ctypes import WinDLL, create_string_buffer
import os
import sys

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(FILE_DIR, "..", "..", "x64", "PriorScientificSDK.dll")

if os.path.exists(path):
    SDKPrior = WinDLL(path)
else:
    raise RuntimeError("DLL could not be loaded.")

rx = create_string_buffer(1000)
encoders = True

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

def retCmd(msg):
    # use if you expect a return value
    print(msg)
    ret = SDKPrior.PriorScientificSDK_cmd(
        sessionID, create_string_buffer(msg.encode()), rx
    )
    return rx.value.decode()  

def GoTo(coord):
    
    cmd("controller.stage.goto-position %d %d" % (coord[0], coord[1]))
    return


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


# methodology: three tests:
# x-axis to and back for 100 microns, 1000 microns, and 10000 microns
# same with y-axis
# both simultaneously


if encoders:
    print("Connecting...")
    cmd("controller.connect 3")
    # substitute 3 with your com port Id
    fit = retCmd("controller.stage.encoder.xy.fitted.get")
    print("return value for fitted: " + str(fit))
    enabled = retCmd("controller.stage.encoder.xy.enabled.get")
    print("return value for fitted: " + str(enabled))
    with open(os.path.join(FILE_DIR,"log.txt"), "a") as f:
        f.write("Encoders disconnected, fit = " + str(fit) + " enabled = " + str(enabled) + "\n")
    
    GoTo((0,0))

    #x axis
    GoTo((100,0))
    GoTo((0,0))

    GoTo((1000,0))
    GoTo((0,0))

    GoTo((10000,0))
    GoTo((0,0))

    #y axis
    GoTo((0,100))
    GoTo((0,0))

    GoTo((0,1000))
    GoTo((0,0))

    GoTo((0,10000))
    GoTo((0,0))

    #both

    GoTo((100,100))
    GoTo((0,0))

    GoTo((1000,1000))
    GoTo((0,0))

    GoTo((10000,10000))
    GoTo((0,0))
        
    # disconnect cleanly from controller
        

else:
    input("Press ENTER to continue...")

cmd("controller.disconnect")