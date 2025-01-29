import numpy as np
from PIL import Image, ImageEnhance

import cv2
import os
import sys

def SharpandContrast(arr) :
    # returns new image (arr is chilling)
    image = Image.fromarray(arr)
    sharp = ImageEnhance.Sharpness(image)
    contrast = ImageEnhance.Contrast(image)
    sharp.enhance(2).show("100% more sharpness")
    contrast.enhance(2).show("100% more contrast")
    return np.asarray(image)


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
IN_DIR = os.path.join(FILE_DIR, "test") \

jpeg_name = "1.jpg"
jpeg_path = os.path.join(IN_DIR, jpeg_name)

img = Image.open(jpeg_path)
sharp = ImageEnhance.Sharpness(img)
contrast = ImageEnhance.Contrast(img)
sharp.enhance(1.5).show()
sharp.enhance(2).show()

"""
for i in range(1,5):
    jpeg_name = "{}.jpg".format(i)
    jpeg_path = os.path.join(IN_DIR, jpeg_name)
    imgnp = cv2.imread(jpeg_path)
    SharpandContrast(imgnp)
    """
