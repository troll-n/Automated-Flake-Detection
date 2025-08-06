"""
Authored by Patrick Kaczmarek\n
Image utilities; what else would be in here?
"""

import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

def arrRight(arr1, arr2):
    """
    Merge two images into one, displayed as second right of first. Inputs arrays.
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

def imgRight(image1, image2):
    """
    Merge two images into one, displayed as second right of first. Inputs images.
    Arguments:
        param image1: first image as a PIL image class
        param image2: second image as a PIL image class
    Returns:
        The merged image as a PIL image class
    """

    (width1, height1) = image1.size
    (width2, height2) = image2.size
    assert(height1==height2)

    result_width = width1 + width2
    result_height = max(height1, height2)

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(width1, 0))
    return result

def arrDown(arr1, arr2):
    """
    Merge two images into one, displayed as second down of first. Inputs arrays.
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

def imgDown(image1, image2):
    """
    Merge two images into one, displayed as second down of first. Inputs images.
    Arguments:
        param image1: first image as a PIL image class
        param image2: second image as a PIL image class
    Returns:
        The merged image as a PIL image class
    """


    (width1, height1) = image1.size
    (width2, height2) = image2.size
    assert(width1 == width2)

    result_width = max(width1, width2)
    result_height = height1 + height2

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, height1))
    return result

def normalize_Gr(img, normalizeTo, regular = True):
    """
    Eureka or whatever
    I have no clue why this works
    """
    avg_color = (0,0,0)
    if regular:
        # this is the regular one just define the average color like usual
        avg_color = (173,175,176) # unironically just a shade of gray
    else:
        # calculate the average color of the normalizeTo img (really not reccomended for optimization reasons)
        avg_color_per_row = np.average(normalizeTo, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        for x in range(0,3):
            avg_color[x] = round(avg_color[x])
        print(avg_color)
    
    avgimg= np.full((1200,1920,3), 0,np.uint8)
    avgimg[:] = avg_color
    
    brightersub = cv2.subtract(img,normalizeTo)
    darkersub = cv2.subtract(normalizeTo,img)

    compositeimg = cv2.add(brightersub, avgimg)
    compositeimg = cv2.subtract(compositeimg, darkersub)
    
    return compositeimg

