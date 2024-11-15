"""
Authored by Patrick Kaczmarek\n
Library for merging images; used for creating maps of the chip's surface.\n
Only right and down are strictly necessary for the purposes of this code.\n
"""

import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

def right(arr1, arr2):
    """
    Merge two images into one, displayed as second right of first
    Arguments:
        param arr1: numpy array of first image
        param arr2: numpy array of second image
    Returns:
        The merged image as a numpy array
    """
    image1 = Image.fromarray(arr1)
    image2 = Image.fromarray(arr2)

    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = width1 + width2
    result_height = max(height1, height2)

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(width1, 0))
    return np.asarray(result)

def down(arr1, arr2):
    """
    Merge two images into one, displayed as second down of first
    Arguments:
        param arr1: numpy array of first image
        param arr2: numpy array of second image
    Returns:
        The merged image as a numpy array
    """
    image1 = Image.fromarray(arr1)
    image2 = Image.fromarray(arr2)

    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = max(width1, width2)
    result_height = height1 + height2

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, height1))
    return np.asarray(result)
