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
IN_DIR = os.path.join(FILE_DIR, "..", "contrast_increase", "data") 

"""jpeg_name = "bot.jpg"
jpeg_path = os.path.join(IN_DIR, jpeg_name)

img = Image.open(jpeg_path)
sharp = ImageEnhance.Sharpness(img)
contrast = ImageEnhance.Contrast(img)
"""
jpeg_name = "weird.jpg"
jpeg_path = os.path.join(IN_DIR, jpeg_name)
img = Image.open(jpeg_path)
sharp = ImageEnhance.Sharpness(img)
contrast = ImageEnhance.Contrast(img)
contrast.enhance(2).save(jpeg_path)

"""for i in range(16,58):
    jpeg_name = "tl{}.jpg".format(i)
    jpeg_path = os.path.join(IN_DIR, jpeg_name)
    img = Image.open(jpeg_path)
    sharp = ImageEnhance.Sharpness(img)
    contrast = ImageEnhance.Contrast(img)
    contrast.enhance(2).save(jpeg_path)"""

