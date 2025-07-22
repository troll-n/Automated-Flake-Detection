"""
MUCH OF THE FUNCTIONAL CODE IS STRIPPED FROM THE FOLLOWING REPO: https://github.com/Ayanava2000/Microscope_Automation
ADAPTED FOR USE WITH THE PRIOR CONTROLLER 3 IN COMBINATION WITH THE Z-FOCUS
"""

import math
import time
import warnings
import numpy as np

import cv2
import random
import os

# stage
from stage_wrapper import Stage
# Blackfly camera
from rotpy.system import SpinSystem
from rotpy.camera import CameraList


#anisotropic diffraction function
def anisodiff(img,niter=1,kappa=50,gamma=0.1,step=(1.,1.),option=1,ploton=False):
    """
    Anisotropic diffusion.
 
    Usage:
    imgout = anisodiff(im, niter, kappa, gamma, option)
 
    Arguments:
            img    - input image
            niter  - number of iterations
            kappa  - conduction coefficient 20-100 ?
            gamma  - max value of .25 for stability
            step   - tuple, the distance between adjacent pixels in (y,x)
            option - 1 Perona Malik diffusion equation No 1
                     2 Perona Malik diffusion equation No 2
            ploton - if True, the image will be plotted on every iteration
 
    Returns:
            imgout   - diffused image.
 
    kappa controls conduction as a function of gradient.  If kappa is low
    small intensity gradients are able to block conduction and hence diffusion
    across step edges.  A large value reduces the influence of intensity
    gradients on conduction.
 
    gamma controls speed of diffusion (you usually want it at a maximum of
    0.25)
 
    step is used to scale the gradients in case the spacing between adjacent
    pixels differs in the x and y axes
 
    Diffusion equation 1 favours high contrast edges over low contrast ones.
    Diffusion equation 2 favours wide regions over smaller ones.
 
    Reference: 
    P. Perona and J. Malik. 
    Scale-space and edge detection using ansotropic diffusion.
    IEEE Transactions on Pattern Analysis and Machine Intelligence, 
    12(7):629-639, July 1990.
 
    Original MATLAB code by Peter Kovesi  
    School of Computer Science & Software Engineering
    The University of Western Australia
    pk @ csse uwa edu au
    <http://www.csse.uwa.edu.au>
 
    Translated to Python and optimised by Alistair Muldal
    Department of Pharmacology
    University of Oxford
    <alistair.muldal@pharm.ox.ac.uk>
 
    June 2000  original version.       
    March 2002 corrected diffusion eqn No 2.
    July 2012 translated to Python
    """
 
    # ...you could always diffuse each color channel independently if you
    # really want
    if img.ndim == 3:
        warnings.warn("Only grayscale images allowed, converting to 2D matrix")
        img = img.mean(2)
 
    # initialize output array
    img = img.astype('float32')
    imgout = img.copy()
 
    # initialize some internal variables
    deltaS = np.zeros_like(imgout)
    deltaE = deltaS.copy()
    NS = deltaS.copy()
    EW = deltaS.copy()
    gS = np.ones_like(imgout)
    gE = gS.copy()
 
    # create the plot figure, if requested
    if ploton:
        import pylab as pl
        from time import sleep
 
        fig = pl.figure(figsize=(20,5.5),num="Anisotropic diffusion")
        ax1,ax2 = fig.add_subplot(1,2,1),fig.add_subplot(1,2,2)
 
        ax1.imshow(img,interpolation='nearest')
        ih = ax2.imshow(imgout,interpolation='nearest',animated=True)
        ax1.set_title("Original image")
        ax2.set_title("Iteration 0")
 
        fig.canvas.draw()
 
    for ii in xrange(niter):
 
        # calculate the diffs
        deltaS[:-1,: ] = np.diff(imgout,axis=0)
        deltaE[: ,:-1] = np.diff(imgout,axis=1)
 
        # conduction gradients (only need to compute one per dim!)
        if option == 1:
            gS = np.exp(-(deltaS/kappa)**2.)/step[0]
            gE = np.exp(-(deltaE/kappa)**2.)/step[1]
        elif option == 2:
            gS = 1./(1.+(deltaS/kappa)**2.)/step[0]
            gE = 1./(1.+(deltaE/kappa)**2.)/step[1]
 
        # update matrices
        E = gE*deltaE
        S = gS*deltaS
 
        # subtract a copy that has been shifted 'North/West' by one
        # pixel. don't as questions. just do it. trust me.
        NS[:] = S
        EW[:] = E
        NS[1:,:] -= S[:-1,:]
        EW[:,1:] -= E[:,:-1]
 
        # update the image
        imgout += gamma*(NS+EW)
 
        if ploton:
            iterstring = "Iteration %i" %(ii+1)
            ih.set_data(imgout)
            ax2.set_title(iterstring)
            fig.canvas.draw()
            # sleep(0.01)
 
    return imgout

# Function  to calculate the Image Quality Metric
# frame_new is an image but i don't know what kind of image, is it a cv2 opened image? (yes)
def img_grad(frame_new):
    prewitt_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]) / 3
    prewitt_y = np.transpose(prewitt_x)

    # kernel_avg = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) / 9

    # frame_new = cv2.filter2D(frame_new, ddepth=-1, kernel=kernel_avg)
    frame_new = anisodiff(frame_new, niter=1, kappa=50, gamma=0.1, step=(1., 1.), option=1, ploton=False)

    grad_x = cv2.filter2D(frame_new, ddepth=-1, kernel=prewitt_x)

    grad_y = cv2.filter2D(frame_new, ddepth=-1, kernel=prewitt_y)

    grad_val_matrix = np.sqrt(grad_x ** 2 + grad_y ** 2)
    grad_val_matrix = np.array(grad_val_matrix, dtype=np.float64)

    # grad_val_matrix_mag = np.average(grad_val_matrix)

    # grad_prod_matrix = 2 * grad_x * grad_y
    # grad_prod_matrix_val = np.average(grad_prod_matrix)

    # score1 = np.average(grad_val_matrix)
    score = np.std(grad_val_matrix)
    # score = 2 ** score
    # score = score1 * score2

    # cv2.imshow("img", grad_val_matrix)

    return score

# Function to open the video camera
def get_frame(camera):
    camera.begin_acquisition()
    image_cam = camera.get_next_image()
    curr_image = image_cam.deep_copy_image(image_cam)
    image_cam.release()
    camera.end_acquisition()
    curr_image.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
    curr_image.set(cv2.CAP_PROP_FRAME_HEIGHT, 1920)
    time.sleep(1)
    ret, frame = curr_image.read()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.resize(frame_gray, (64, 64))
    # vid.release()
    return frame_gray


def show():
    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1500)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 750)
    ret, frame = video.read()
    cv2.imshow('frame', frame)
    video.release()

# calculates score of current frame
def cal_score():
    sum_score1 = 0
    sum_score2 = 0

    for i in range(0, 2):
        frame = get_frame()
        score = img_grad(frame)
        sum_score1 += score
        # sum_score2 += score2
    score = sum_score1 / 2
    # score2 = sum_score2 / 2

    return score

# Autofocus Algorithm
def focus(stage, num_itrs, min_step, max_step, checkpoint_itr):
    itr_array = []
    itr = num_itrs
    net_rotation = 0
    best_score_pos = 0
    top_score = 0
    step_size = 0
    focus_dir = 1
    for i in range(1, itr + 1):
        score = cal_score()
        if i == 1:
            first_score = score
        if score > top_score:
            top_score = score
            best_score_pos = net_rotation

        if i >= checkpoint_itr:
            if score < top_score:
                print(
                    f"Iteration : {i}, Step size = {step_size}, score = {score}, Net Rotation: {net_rotation}")
                break
        step_size = random.randint(min_step, max_step)
        motor_fine_focus.rotate()
        print(
            f"Iteration : {i}, Step size = {step_size}, score = {score}, Net Rotation: {net_rotation}")
        step_size = random.randint(min_step, max_step)
        net_rotation += step_size
        motor_fine_focus.rotate()

        itr_array.append(i * -1)

    print(f"Current motor direction is {motor_fine_focus.direction}")
    focus_dir = 0 - focus_dir #change the direction we're going in on the focus
    print(f"Motor rotation direction changed to {motor_fine_focus.direction}")
    step_size = net_rotation
    print(f"Motor going back to the starting position. Rotating {step_size}"
          f" steps in direction :{motor_fine_focus.direction}")
    motor_fine_focus.rotate()
    print("Starting position reached")
    score = cal_score()
    print(f"score is {score}, first score was {first_score}")
    print(f"absolute diff is {abs(score - first_score)}")

    difference = abs(score - first_score)
    while difference > 0.5:
        step_size = 5
        motor_fine_focus.rotate()
        score = cal_score()
        if score > first_score:
            print(f"score becomes greater than the initial score.")
            break
        difference = abs(score - first_score)
        print(f"score is {score}, difference is {difference}")

    net_rotation = 0
    itr = num_itrs
    step_size = 0
    for i in range(1, itr + 1):

        score = cal_score()
        if score > top_score:
            top_score = score
            best_score_pos = net_rotation

        if i >= checkpoint_itr:
            if score < top_score:
                print(
                    f"Iteration : {i}, Step size = {step_size}, score = {score}, Net Rotation: {net_rotation}")
                break

        print(
            f"Iteration : {i}, Step size = {step_size}, score = {score}, Net Rotation: {net_rotation}")
        step_size = random.randint(min_step, max_step)
        net_rotation -= step_size
        motor_fine_focus.rotate()

        itr_array.append(i * 1)

    print(f"All iterations completed. The best score of {top_score} at {best_score_pos} steps")
    print(f"Going to the best score location")
    print(f"Current motor direction is {motor_fine_focus.direction}")
    focus_dir = 0 - focus_dir #change the direction we're going in on the focus
    print(f"Motor direction changed to {motor_fine_focus.direction}")
    time.sleep(2)
    step_size = abs(net_rotation - best_score_pos)
    print(f"Rotating {step_size} steps to reach the best location ")
    motor_fine_focus.rotate()
    # time.sleep(2)
    print("Best location reached")

    last_score = cal_score()
    print(f"Final score is {last_score}")

    # focus_dir = 0 - focus_dir #change the direction we're going in on the focus
    last_diff = abs(last_score - top_score)
    step_size = 3
    motor_fine_focus.rotate()
    score = cal_score()
    diff = abs(score - top_score)
    print(f"last difference was {last_diff}, current difference is {diff}")

    if diff > last_diff:
        if score > top_score:
            pass
        else:
            print(f"Motor direction is {motor_fine_focus.direction}")
            focus_dir = 0 - focus_dir #change the direction we're going in on the focus
            print(f"New motor direction is {motor_fine_focus.direction}")

    while diff > 0.5:
        step_size = 3
        motor_fine_focus.rotate()
        score = cal_score()
        diff = abs(score - top_score)
        if score < top_score:
            focus_dir = 0 - focus_dir #change the direction we're going in on the focus
            step_size = 3
            motor_fine_focus.rotate()
            time.sleep(2)
            motor_fine_focus.rotate()
            break

        print(f"score is {score}, difference is {diff}")

    top_score = cal_score()
    print(f"Best score is {top_score}")


'''
    print("Motor rotates...")
    step_size = 3
    motor_fine_focus.rotate()
    #score = cal_score()
    #print(f"New score is {score}, best score was {top_score}")

    while True:
        score = cal_score()
        print(f"New score is {score}, best score was {top_score}")
        
        if score < top_score:
            focus_dir = 0 - focus_dir #change the direction we're going in on the focus
            step_size = 3
            motor_fine_focus.rotate()
            time.sleep(2)
            motor_fine_focus.rotate()
            score = cal_score()
            if score < top_score:
                focus_dir = 0 - focus_dir #change the direction we're going in on the focus
                step_size = 3
                motor_fine_focus.rotate()
                print("Best position reached.")
                print(f"Final score is {cal_score()}")
                break

        if score > top_score:
            step_size = 3
            motor_fine_focus.rotate()
            top_score = score
'''

# ##############################################################################################################################################################################################################

motor_fine_focus = microscope_motor(8, 9, 0.00001)

focus(50, 15, 15, 12)
