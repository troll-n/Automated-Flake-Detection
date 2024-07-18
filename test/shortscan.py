"""
Author: Patrick Kaczmarek
Copy of demo/demo.py with the aim to return a scan as fast as possible
"""
import argparse
import json
import os

import cv2
import numpy as np

from demo.demo_functions import visualise_flakes
from GMMDetector import MaterialDetector

import time


# I want the args done; customizability is low priority
def arg_parse() -> dict:
    """
    Parse arguments to the detect module

    Returns:
        dict: Dictionary of arguments
    """
    # fmt: off
    parser = argparse.ArgumentParser(description="2DMatGMM Demo")
    parser.add_argument("--out", dest="out", help="Output directory", default="output", type=str)
    parser.add_argument("--num_image", dest="num_image", help="Number of images to process", default=10, type=int)
    parser.add_argument("--material", dest="material", help="Material to process", default="Graphene", type=str)
    parser.add_argument("--size", dest="size", help="Size threshold in pixels", default=200, type=int)
    parser.add_argument("--std", dest="std", help="Standard deviation threshold", default=5, type=float)
    parser.add_argument("--min_confidence", dest="min_confidence", help="The Confidence threshold", default=0.5, type=float)
    parser.add_argument("--channels", dest="channels", help="Channels to use", default="BGR", type=str)
    parser.add_argument("--shuffel", dest="shuffel", default=True, type=bool)
    # fmt: on
    return vars(parser.parse_args())


args = arg_parse()

# Constants
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRAST_PATH_ROOT = os.path.join(FILE_DIR, "..", "GMMDetector", "trained_parameters")
DATA_DIR = os.path.join(FILE_DIR, "..", "Datasets", "GMMDetectorDatasets")
OUT_DIR = os.path.join(FILE_DIR, args["out"])
os.makedirs(OUT_DIR, exist_ok=True)

NUM_IMAGES = args["num_image"]
MATERIAL = args["material"]
SIZE_THRESHOLD = args["size"]
STD_THRESHOLD = args["std"]

# loads up the contrast dictionary for whatever material we want
with open(os.path.join(CONTRAST_PATH_ROOT, f"{MATERIAL}_GMM.json")) as f:
    contrast_dict = json.load(f)

# makes a model object
model = MaterialDetector(
    # passes constrast_dict that we made above
    contrast_dict=contrast_dict,
    # size threshold in pixels, 200 nm
    size_threshold=SIZE_THRESHOLD,
    standard_deviation_threshold=STD_THRESHOLD,
    used_channels="BGR",
)

# load the images and shuffel them so we dont always sample the same images
image_directory = os.path.join(DATA_DIR, MATERIAL, "test_images")
image_names = os.listdir(image_directory)
if args["shuffel"]:
    np.random.shuffle(image_names)
used_images = image_names[:NUM_IMAGES]



# this takes the most time
for image_name in used_images:
    #path to image
    image_path = os.path.join(image_directory, image_name)
    #cv2 is a package for computer vision
    #imread loads the image as an array
   
    image = cv2.imread(image_path)
    
    #list of flakes returned by the model (doesn't take the most time? 0.05 s???)
    start_time = time.time()
    flakes = model(image)
    with open(os.path.join(FILE_DIR,"log.txt"), "a") as f:
        f.write((time.ctime() + ": It took " + str(time.time() - start_time) + "to scan " + image_name + "\n"))
    
    
    #
    image_overlay = visualise_flakes(flakes, image, args["min_confidence"])
    # saves the image
    cv2.imwrite(os.path.join(OUT_DIR, image_name), image_overlay)
