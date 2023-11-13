import cv2
import math
import numpy as np
from collections import defaultdict
import sys
from newDroplet import NewDroplet

sys.path.append('../api')
sys.path.append('../settings')

# from configuration import CAMERA_ID

other_start_position = None
salt_position = None

window_size = (1280, 720)

# # RED COLOR DEFINITION
# lower = np.array([0, 40, 40])
# lower2 = np.array([140, 40, 40])
# upper = np.array([8, 255, 255])
# upper2 = np.array([180, 255, 255])

lower = np.array([0, 40, 40])
upper = np.array([8, 255, 255])

lower2 = np.array([140, 40, 40])
upper2 = np.array([180, 255, 255])

# SETTINGS
SENSITIVITY_VALUE = 20  # Blurring function parameter
BLUR_SIZE = 14  # Blurring function parameter

MIN_AREA = 5  # Minimum area for droplets to be recognized
MOVEMENT_TOLERANCE = 2  # Limit for updating droplet position
AREA_TOLERANCE = 30  # Limit of area change for updating
DIST_TOLERANCE = 30  # Limit to decide if the droplet is a new droplet or it is an existing one
left_safe_area = False  # For the analysis of the path, variable that indicates if the droplet has left the safe area

debug_mode = False
recording = False

date = ""
fourCC = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')


def float_euclidean_dist(p, q):
    """This function returns the euclidean distance between two points"""
    px, py = p[0], p[1]
    qx, qy = q[0], q[1]
    diff_x = abs(qx - px)
    diff_y = abs(qy - py)
    return float(math.sqrt((diff_x * diff_x) + (diff_y * diff_y)))


def find_repeat(numbers):
    seen = set()
    for num in numbers:
        if num in seen:
            return num
        seen.add(num)


class MultiDropletTracking:
    def __init__(self):
        self.x = None
        self.y = None
        self.paths = defaultdict(list)
        self.distances = defaultdict(list)
        self.droplets = []
        self.previousDroplets = []
        self.biggestIDInit = -1  # id of the biggest droplet at startup. If the droplet size changes, it still tracks
        # the same id, not the new biggest
        self.isBiggestIDInit = False
        self.biggestID = 0
        self.frame_counter = 0

    def get_similar_index(self, drop):
        self.distances = []
        for c in range(0, len(self.previousDroplets)):
            distance = float_euclidean_dist(self.previousDroplets[c].centroid, drop.centroid)
            self.distances.append(distance)

        if min(self.distances) < DIST_TOLERANCE:
            min_dist = 100000000
            i = 0
            for d in self.distances:
                if d < min_dist:
                    min_dist = d
                    index = i
                i += 1
            iD = self.previousDroplets[index].dropId
            return iD
        else:
            return -1

    def was_in_the_array(self, drop):  # IMPROVABLE
        for drp in self.previousDroplets:
            distance = float_euclidean_dist(drp.centroid, drop.centroid)
            if distance < DIST_TOLERANCE:
                return True
        return False

    def track(self, thresh_image, result, color):
        biggestArea = 0
        self.biggestID = 0
        self.isBiggestIDInit = False
        # Finds the contours_list in the image
        _, contours_list, hierarchy = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # contours_list is a np array with coordinates of points around the droplet
        drop_count = 0  # FAI
        current_droplets = []
        for contours in contours_list:
            moments_dictionary = cv2.moments(contours)
            area = moments_dictionary['m00']
            if area > MIN_AREA:
                centroid = (int(moments_dictionary['m10'] / area), int(moments_dictionary['m01'] / area))
                drop = NewDroplet(drop_count, centroid, contours, color, area)
                drop_count += 1
                current_droplets.append(drop)
                if self.was_in_the_array(drop):
                    index = self.get_similar_index(drop)
                    drop.dropId = index
                    if index == -1:
                        print "ERROR"
                        exit()
                else:
                    self.droplets.append(drop)
                    drop.dropId = len(self.droplets)
                # Check for repeated droplets id
                repeat = True
                while repeat:
                    id_list = []
                    for drp in current_droplets:
                        id_list.append(drp.dropId)
                    number = find_repeat(id_list)
                    if number:
                        print "duplicated"
                        drop1 = []
                        for drp in current_droplets:
                            if drp.dropId == number:
                                if not drop1:
                                    drop1 = drp
                                else:
                                    drop2 = drp
                        print "drop1: " + str(drop1.dropId) + "centroid " + str(drop1.centroid)
                        print "drop2: " + str(drop2.dropId) + "centroid " + str(drop2.centroid)
                        if drop1.area > drop2.area:
                            self.droplets.append(drop2)
                            drop2.dropId = len(self.droplets)
                        else:
                            self.droplets.append(drop1)
                            drop1.dropId = len(self.droplets)

                    else:
                        repeat = False

                # Calculate the biggest droplet in the current frame:
                if drop.area > biggestArea:
                    biggestArea = drop.area
                    self.biggestID = drop.dropId
                    if self.frame_counter == 0:
                        self.biggestIDInit = drop.dropId
                # Calculate if the biggest droplet at init is still there
                if drop.dropId == self.biggestIDInit:
                    self.isBiggestIDInit = True
                self.paths[drop.dropId].append(drop.centroid)  # append droplet centroid to it's droplet in the array
                cv2.drawContours(result, contours, -1, (0, 255, 0), 1)
                # message = "Color : " + str(color)
                message = "Id : " + str(drop.dropId)
                # cv2.putText(result, message, centroid, cv2.FONT_HERSHEY_SIMPLEX, .5, 255)

        self.previousDroplets = current_droplets
        self.frame_counter += 1

    def get_biggest_path(self):
        return self.paths[self.biggestID]

    def get_path_biggest_init(self):
        return self.isBiggestIDInit, self.paths[self.biggestIDInit]

    def do_track(self, frame, result):
        """ One shot: identify the droplet and display it in the image """
        # Image blurring and threshold
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # RED TRACKING

        thresh_image = cv2.bitwise_or(cv2.inRange(frame_hsv, lower, upper), cv2.inRange(frame_hsv, lower2, upper2))
        cv2.blur(thresh_image, (5, 5), thresh_image)
        cv2.threshold(thresh_image, 0, 255, cv2.THRESH_OTSU)
        cv2.morphologyEx(thresh_image, cv2.MORPH_OPEN, (20, 20), thresh_image)
        cv2.morphologyEx(thresh_image, cv2.MORPH_CLOSE, (20, 20), thresh_image)
        # cv2.imshow('Threshold Image', thresh_image)
        self.track(thresh_image, result, "red")

    def get_paths(self):
        return self.paths

    def show_output_biggest(self, result):
        max_area = 0
        biggest_droplet = 0
        starting_point = 0
        ending_point = 0
        for i, drp in enumerate(self.droplets):
            if drp.area > max_area:
                max_area = drp.area
                biggest_droplet = drp.dropId
                starting_point = drp.path[0]
                last_point = len(self.paths[drp.dropId]) - 1
                ending_point = self.paths[drp.dropId][last_point]

        for index, centroid in enumerate(self.paths[biggest_droplet]):
            cv2.circle(result, centroid, 1, (255, 0, 0), 1)
            if index == 0:
                print('start', centroid)
                text_position = (centroid[0], centroid[1] + 11)
                cv2.putText(result, "BEGIN", text_position, cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            elif index == len(self.paths[biggest_droplet]) - 1:
                print('end', centroid)
                text_position = (centroid[0], centroid[1] + 11)
                cv2.putText(result, "END", text_position, cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
        return starting_point, ending_point, max_area

    def add_text_on_screen(self, result, text):
        cv2.putText(result, text,
                    (150, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255))

    def show_output(self, result):
        for i, drp in enumerate(self.droplets):
            for index, c in enumerate(self.paths[drp.dropId]):
                cv2.circle(result, c, 1, (255, 0, 0), 1)
                if index == 0:
                    text_position = (c[0], c[1] + 8)
                    cv2.putText(result, "BEGIN " + str(drp.dropId), text_position, cv2.FONT_HERSHEY_SIMPLEX, .3, 255)
                elif index == len(self.paths[drp.dropId]) - 1:
                    text_position = (c[0], c[1] + 8)
                    cv2.putText(result, "END " + str(drp.dropId), text_position, cv2.FONT_HERSHEY_SIMPLEX, .3, 255)
        return
