#! /usr/bin/python
import sys

sys.path.append('../../settings')
sys.path.append('../../api')
from multiDropletTracking import MultiDropletTracking
import numpy as np
import cv2
import VisionTools as vT
import datetime
import time
import os
import math
from syringe import Syringe
from datalogger import DataLogger
from evobot import EvoBot
sys.path.append('../../api')
sys.path.append('../../settings')
from configuration import *

__author__ = "anfv"
__date__ = "$17-Sep-2016 17:39:28$"

if __name__ == "__main__":
    print "Multi Droplet Tracking Example"


def _calculate_pitagora(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2.0) + ((a[1] - b[1]) ** 2.0))

usrmsglogger = DataLogger()
evobot = EvoBot(PORT_NO, usrmsglogger)
decanol_syringe = Syringe(evobot, SYRINGES['SYRINGE4'])

# Choose a number between 1 and 7 to track one example
number = 12

# height and width of the video stream
height = 720
width = 1280

filename = str(number) + ".mp4"

# Video to open
cap = cv2.VideoCapture(filename)


# Petridish center and diameter in pixels
# petridishCenter = (235, 430) # 0
# petridishCenter = (519, 430)  # 1
# petridishCenter = (799, 430)  # 2
# petridishCenter = (1080, 430) # 3
petridishCenter = (235, 148)  # 4
# petridishCenter = (518, 150) # 5
# petridishCenter = (799, 150) # 6

# petridishCenter = (1080, 150) # 7


# x_center, y_center = (193, 154)  #0
# x_center, y_center = (193, 252)  #1
# x_center, y_center = (193, 350)  #2
# x_center, y_center = (193, 448)  #3
x_center, y_center = (97, 154)  #4
# x_center, y_center = (97, 252)  #5
# x_center, y_center = (97, 350)  #6
# x_center, y_center = (97, 448)  #7

petridishDiameter = 254

salt_pos = (petridishCenter[0] - 59, petridishCenter[1]-1)

# fourCC = cv2.VideoWriter_fourcc(*'XVID')
fourCC = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # for mac user
window_size = (height, width)

cap.set(3, height)  # Set to the resoluton of the video or camera
cap.set(4, width)  # Set to the resoluton of the video or camera

ret, frame = cap.read()

if ret == 0:
    print 'ERROR READING INPUT'

x, y, z = frame.shape
mask = np.zeros((x, y, 3), np.uint8)

experiment_time = 600
# Record the video of the identified droplets
recording = False

if recording:
    date = str(datetime.datetime.now())
    file_name = os.path.join(FILE_PATH, "%s_video.avi" % vT.removeColon(date))
    out = cv2.VideoWriter(file_name, fourCC, 10.0, window_size)

start_tracking_time = datetime.datetime.now()

# Init the class MultiDropletTracking
trackObject = MultiDropletTracking()

left_safe_area = False  # For the analysis of the path, variable that indicates if the droplet has left the safe area
# Loop to take a frame and track the droplets
while True:
    ret, frame = cap.read()  # Read a new frame
    if ret == 0:
        print "ERROR READING INPUT"
        break

    # Make a copy of the current frame
    result = frame.copy()

    # Draw a circle around the Petri dish object
    cv2.circle(result, petridishCenter, petridishDiameter / 2, (0, 255, 0), 2)

    # Create a mask to only track droplets inside the Petri dish
    mask.fill(0)
    cv2.circle(mask, petridishCenter, petridishDiameter / 2, (255, 255, 255), -1)
    frame = cv2.bitwise_and(frame, mask)

    # Remove all the noise (erosion and dilation)
    kernel = np.ones((2, 2), np.uint8)
    frame = cv2.erode(frame, kernel, iterations=1)
    # frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    # Perform the tracking
    trackObject.do_track(frame, result)

    #  Analysis of the path #

    # Radius of the safe are around the starting position where the direction of the droplet is irrelevant
    RADIUS_START = 30
    ANALISYS_FRAME = 8  # Number of frames between the current pos and the pos used to calculate the direction
    # Max angle that is allowed between the (droplet direction angle) and (droplet-salt angle)
    ANGLE_TH = 55.0 / 180.0 * math.pi
    FILTER_VALUE = 0.8
    DIST_TH = 8.0
    frame_droplet_left_safe = 0  # Var used to indicate the frame where the droplet leaves the safe area

    # Get path
    is_droplet, path = trackObject.get_path_biggest_init()
    if is_droplet is False:
        # The droplet has disappear, stop tracking
        break

    # Get start coordinates and draw a circle around the start and final position
    start_coordinates = path[0]
    cv2.circle(result, start_coordinates, RADIUS_START, (0, 255, 0), 1)
    cv2.circle(result, salt_pos, 10, (0, 255, 0), 1)

    # If we are in the safe area, do nothing
    current_pos = path[len(path) - 1]
    distance = pow((current_pos[0] - start_coordinates[0]) ** 2 + (current_pos[1] - start_coordinates[1]) ** 2, 0.5)
    if distance < RADIUS_START and not left_safe_area:
        frame_droplet_left_safe = len(path) - 1
    else:
        # The droplet has abandoned the safe area

        if len(path) - 1 - ANALISYS_FRAME - frame_droplet_left_safe > -1:
            # There are enough frames after the droplet left the safe area
            last_pos = path[len(path) - 1 - ANALISYS_FRAME]
            moved_dist = pow((current_pos[0] - last_pos[0]) ** 2 + (current_pos[1] - last_pos[1]) ** 2, 0.5)
            curr_dir = math.atan2(current_pos[1] - last_pos[1], current_pos[0] - last_pos[0])
            salt_dir = math.atan2(salt_pos[1] - last_pos[1], salt_pos[0] - last_pos[0])
            angle_dif = curr_dir - salt_dir
            if angle_dif > math.pi:
                angle_dif -= 2.0 * math.pi
            if angle_dif < -math.pi:
                angle_dif += 2.0 * math.pi
            if left_safe_area == False:
                #This is the first time that the droplet is outside safe are
                previous_angle_dif = angle_dif
            else:
                #Filter the angle
                angle_dif = previous_angle_dif*(1-FILTER_VALUE) + angle_dif*FILTER_VALUE
            left_safe_area = True
            # print str(round(curr_dir*180.0/math.pi, 1)) + "\t" + str(round(salt_dir*180.0/math.pi, 1)) + "\t
            # " + str(round(angle_dif*180.0/math.pi, 1)) + "\t" + str(moved_dist)
            if abs(angle_dif) > ANGLE_TH and moved_dist > DIST_TH:
                print "Aborted, droplet is not going towards the salt"
                end_tracking_time = datetime.datetime.now()
                break

    # END OF ANALYSIS OF THE PATH #

    # Waits up to other 30ms for a keypress
    # If none -> -1
    key = cv2.waitKey(30) & 0xFF

    now = datetime.datetime.now()
    if (start_tracking_time + datetime.timedelta(seconds=experiment_time)) <= now:
        # If the time is gone, quit
        print "Stopped"
        end_tracking_time = now
        break
    elif key == ord('q'):
        # If q is pressed, quit
        print "Aborted"
        end_tracking_time = now
        break

    if recording:
        out.write(result)
    cv2.imshow('Multidroplet Tracking', result)
    time.sleep(.2)

# END WHILE TRUE

initial_point_s, ending_point_s, droplet_area = trackObject.show_output_biggest(result)
point_i = np.float32([initial_point_s[0], initial_point_s[1], 1])
rob_cor_i = np.dot(decanol_syringe.affineMat, point_i)
initial_point = (rob_cor_i[0].item(), rob_cor_i[1].item())
print "Coordinates of the initial point of the droplet (mm): " + str(initial_point)

point_e = np.float32([ending_point_s[0], ending_point_s[1], 1])
rob_cor_e = np.dot(decanol_syringe.affineMat, point_e)
ending_point = (rob_cor_e[0].item(), rob_cor_e[1].item())
print "Coordinates of the end point of the droplet (mm): " + str(ending_point)

print "The droplet area is: " + str(droplet_area)


print 'the coordinates of the center of the petridish are: ' + str((x_center, y_center), )

edge_check = _calculate_pitagora((x_center, y_center), ending_point)
print 'FUCK THIS SHIT'
print 'this is the START POINT: ' + str(initial_point)
print 'this is the edge check: ' + str(edge_check)
# check if the distance done by the droplet is smaller than the radius of the petridish

droplet_diameter = math.sqrt(droplet_area / 3.14) * 2.0
print 'the diameter of the droplet is: ' + str(droplet_diameter)
radius_mm = 129.0

limit_edge = radius_mm - (droplet_diameter / 2.86)
print 'this is the limit edge : ' + str(limit_edge)

if edge_check < limit_edge:
    # the end point is within the distance
    fitness_value = _calculate_pitagora(initial_point, ending_point) / \
                            (_calculate_pitagora(ending_point, salt_pos) + (2.0 * radius_mm))
    print 'not at border'
else:
    fitness_value = 0.0
    print 'at border'

print "the fitness value registered is %f" % fitness_value

# Show the results
copyFrame = result.copy()
copyFrame2 = result.copy()
trackObject.show_output(copyFrame)
cv2.imshow('Tracks of all the droplets', copyFrame)

# Show the result of the biggest droplet and give its init and end positions
initPos, endPos, area = trackObject.show_output_biggest(copyFrame2)
cv2.imshow('Track of the biggest droplet', copyFrame2)
print "init position of the biggest droplet: " + str(initPos)
print "end position of the biggest droplet: " + str(endPos)

# gets all the paths of all the droplets
paths = trackObject.get_paths()

if recording:
    date = str(datetime.datetime.now())
    file_name = os.path.join(FILE_PATH, "%s_screen_OLDfitness%f.jpg" % (vT.removeColon(date), fitness_value))
    cv2.imwrite(file_name, result)
    out.release()

cv2.waitKey(0)
cv2.destroyAllWindows()
