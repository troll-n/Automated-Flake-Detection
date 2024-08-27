import os
import cv2
import numpy as np
from rotpy.system import SpinSystem
from rotpy.camera import CameraList
# create system/camera list instance and create the camera by serial number
system = SpinSystem()
cameras = CameraList.create_from_system(system, True, True)
cameras.get_size()
camera = cameras.create_camera_by_serial('23309234') # get camera serial ###
# init so we can read the pixel format node
camera.init_cam()
# the names of the pixel formats available for the camera
camera.camera_nodes.PixelFormat.get_entries_names()
# the current one is BayerRG8
node = camera.camera_nodes.PixelFormat.get_node_value()
node.get_enum_name()
# instead set it to RGB8
camera.camera_nodes.PixelFormat.set_node_value_from_str('BGR8')
camera.camera_nodes.PixelFormat.get_node_value().get_enum_name()
# set acquired image height to 800 pixels
camera.camera_nodes.Height.get_node_value()
# camera.camera_nodes.Height.set_node_value(800)
camera.camera_nodes.Height.get_node_value()
camera.camera_nodes.Height.get_max_value()
# get the current framerate
camera.camera_nodes.AcquisitionFrameRate.is_readable()
camera.camera_nodes.AcquisitionFrameRate.get_node_value()
# get one image and copy and release it so we don't tie up the buffers
camera.begin_acquisition()
image_cam = camera.get_next_image()
image = image_cam.deep_copy_image(image_cam)
image_cam.release()
camera.end_acquisition()
# get some image metadat
image.get_frame_timestamp() / 1e9
512.51940629
image.get_height()
800
image.get_buffer_size()
image.get_pix_fmt()
'RGB8'
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
image.save_png(os.path.join(FILE_DIR, 'testimg.png'))
# cleanup
camera.deinit_cam()
camera.release()