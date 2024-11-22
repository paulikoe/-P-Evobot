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
from configuration import *

__author__ = "capo"
__date__ = "$7-Jul-2017 15:03:00$"

number = 10

if __name__ == "__main__":
    print "Multi Droplet Tracking Example with Fitness computer every step number individual %d" % number

path_file = '/Users/capo/Desktop/my_folder/tritonx_second_ftness_2oct/'


def _compute_distance(a, b):
    """this function computes the euclidean distance between two points
    :param
    a: tuple of point
    b: tuple of point
    """
    return math.sqrt(((a[0] - b[0]) ** 2.0) + ((a[1] - b[1]) ** 2.0))


# Choose a number between 1 and 7 to track one example


# height and width of the video stream
height = 720
width = 1280

filename = str(number) + ".mp4"

# Video to open
cap = cv2.VideoCapture(filename)

length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print length
# Use cap = cv2.VideoCapture(CAMERA_ID) to use the camera like:
# cap = cv2.VideoCapture(0)

# Petridish center and diameter in pixels

if number == 0:
    petridishCenter = (245, 500)  # 0
    x_center, y_center = (193, 154)
elif number == 8:
    petridishCenter = (520, 500)  # 8 peg

    # petridishCenter = (240, 500)  # 8 decanoate
    # petridishCenter = (240, 450)  # 8 triton
    x_center, y_center = (193, 154)
elif number == 1:
    # petridishCenter = (519, 500)  # 1 #decanoate
    petridishCenter = (519, 500)  # 1 #triton
    x_center, y_center = (193, 252)  # 1
elif number == 9:
    petridishCenter = (519, 500)  # 9
    x_center, y_center = (193, 252)  # 9
elif number == 2:
    petridishCenter = (799, 500)  # 2 decanoate
    # petridishCenter = (799, 450)  # 2 triton
    x_center, y_center = (193, 350)  # 2
elif number == 10:
    petridishCenter = (799, 500)  # 10
    # petridishCenter = (1080, 500)  # peg 10
    x_center, y_center = (193, 350)  # 10
elif number == 3:
    petridishCenter = (1080, 500)  # 3
    x_center, y_center = (193, 448)  # 3
elif number == 11:
    # petridishCenter = (1080, 490)  # 11 decanoate
    # petridishCenter = (1080, 500)  # 11 triton
    x_center, y_center = (193, 448)  # 11
    petridishCenter = (245, 220)  # 11 peg

elif number == 4:
    petridishCenter = (245, 220)  # 4
    x_center, y_center = (97, 154)  # 4
    # petridishCenter = (515, 220)  # 12 triton2cmc

elif number == 12:
    # petridishCenter = (235, 220)  # 12 decanoate
    # petridishCenter = (235, 170)  # 12 triton
    x_center, y_center = (97, 154)  # 12
    petridishCenter = (515, 220)  # 12 peg

elif number == 5:
    petridishCenter = (518, 220)  # 5 decanoate
    # petridishCenter = (518, 170)  # 5 tritonx
    x_center, y_center = (97, 252)  # 5
elif number == 13:
    # petridishCenter = (518, 170)  # 13 decanoate
    petridishCenter = (799, 220)  # 13 tritonx
    x_center, y_center = (97, 252)  # 13
elif number == 6:
    petridishCenter = (799, 220)  # 6 decanoate
    # petridishCenter = (799, 170)  # 6 tritonx
    x_center, y_center = (97, 350)  # 6
elif number == 14:
    petridishCenter = (1080, 220)  # 14
    x_center, y_center = (97, 350)  # 14
    # petridishCenter = (799, 220)  # 14
    # x_center, y_center = (97, 350)  # 14
else:
    # petridishCenter = (245, 500)  # 0
    # x_center, y_center = (193, 154)
    petridishCenter = (1080, 220)  # 7
    x_center, y_center = (97, 448)  # 7

petridishDiameter = 254  # in px

# Salt pos in pixels, Use a approximate value for testing
salt_pos = (petridishCenter[0] - 59, petridishCenter[1]-1)

# fourCC = cv2.VideoWriter_fourcc(*'XVID')
fourCC = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # for mac user

window_size = (height, width)

cap.set(3, height)  # Set to the resolution of the video or camera
cap.set(4, width)  # Set to the resolution of the video or camera

ret, frame = cap.read()

if ret == 0:
    print 'ERROR READING INPUT'

x, y, z = frame.shape
mask = np.zeros((x, y, 3), np.uint8)
mask2 = np.zeros((x, y, 3), np.uint8)

experiment_time = 1000000

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

counter = 0.0
frame_counter = 0.0
fitness_value = 0.0

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
    mask2.fill(0)
    cv2.circle(mask, petridishCenter, petridishDiameter / 2, (255, 255, 255), -1)
    cv2.circle(frame, salt_pos, 17, (0, 0, 0), -1)

    frame = cv2.bitwise_and(frame, mask)

    # Perform the tracking
    trackObject.do_track(frame, result)

    #  Analysis of the path #

    # Radius of the safe are around the starting position where the direction of the droplet is irrelevant
    radius_start = 20
    analysis_frame = 8  # Number of frames between the current pos and the pos used to calculate the direction
    # Max angle that is allowed between the (droplet direction angle) and (droplet-salt angle)
    # angle_threshold = 120.0 / 180.0 * math.pi
    filter_value = 0.8

    # distance_threshold_from_salt = 40.0
    distance_threshold = 40.0
    frame_droplet_left_safe = 0  # Var used to indicate the frame where the droplet leaves the safe area

    # Get path
    is_droplet, path = trackObject.get_path_biggest_init()
    if is_droplet is False:
        # The droplet has disappear, stop tracking
        print 'the droplet has disappeared -> tracking stopped'
        break

    # Get start coordinates and draw a circle around the start and final position
    start_coordinates = path[0]
    cv2.circle(result, start_coordinates, radius_start, (0, 255, 0), 1)
    cv2.circle(result, salt_pos, 0, (0, 255, 0), 1)
    # cv2.circle(frame, salt_pos, 15, (0, 0, 0), 10)

    # If we are in the safe area, do nothing
    current_pos = path[len(path) - 1]
    distance_from_start_point = _compute_distance(current_pos, start_coordinates)
    frame_counter += 1.0

    if distance_from_start_point < radius_start and not left_safe_area:
        frame_droplet_left_safe = len(path) - 1
    else:
        # The droplet has abandoned the safe area
        if counter % analysis_frame == 0.0:

            left_safe_area = True
            if len(path) - 1 - analysis_frame - frame_droplet_left_safe > -1:
                # There are enough frames after the droplet left the safe area
                last_pos = path[len(path) - 1 - analysis_frame]

                moved_dist = _compute_distance(current_pos, last_pos)
                curr_dir = math.atan2(current_pos[1] - last_pos[1], current_pos[0] - last_pos[0])
                salt_dir = math.atan2(salt_pos[1] - last_pos[1], salt_pos[0] - last_pos[0])

                fitness_value += moved_dist * math.cos(curr_dir - salt_dir)

                print 'THIS IS THE FITNESS COMPUTED EVERY %d STEP: %f' % (analysis_frame, (fitness_value / frame_counter))

            salt_distance = _compute_distance(current_pos, salt_pos)
            print 'this is the distance to the salt: %f' % salt_distance
            if salt_distance < distance_threshold:
                print "Tracking stopped, droplet has gone in the salt area"
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
    counter += 1

# END WHILE TRUE

if frame_counter == 0.0:
    fitness_value = -0.05
else:
    fitness_value = fitness_value / frame_counter
print 'This is the final fitness value computed: %f' % fitness_value


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

foto = True
if foto:
    date = str(datetime.datetime.now())
    file_name = os.path.join(path_file, "%s_fitness_value_%f_ind_num_%d.jpg" % (vT.removeColon(date), fitness_value, number))
    cv2.imwrite(file_name, copyFrame2)

cv2.waitKey(0)
cv2.destroyAllWindows()
