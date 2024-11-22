import sys

sys.path.append('../api')
sys.path.append('../settings')

# from settings import CAMERA_ID, PORT_NO
from configuration import *

import numpy as np
import cv2
from evobot import EvoBot
from syringe import Syringe
from head import Head
from datalogger import DataLogger
import math
from collections import defaultdict
import datetime
import VisionTools as vt

# RED COLOR DEFINITION
lower = np.array([0, 40, 40])
upper = np.array([8, 255, 255])
lower2 = np.array([140, 40, 40])
upper2 = np.array([180, 255, 255])

# BLUE COLOR DEFINITION
lower_blue = np.array([60, 50, 50])
upper_blue = np.array([160, 255, 255])

other_start_position = None
salt_position = None

start_tracking_time = None
end_tracking_time = None

WINDOW_SIZE = (1280, 720)


# CLASS myDroplet
class MyDroplet:
    def __init__(self, dropId, centroid, contour, color, area):
        self.dropId = dropId
        self.centroid = centroid
        self.contour = contour
        self.color = color
        self.area = area
        paths[self.dropId].append(centroid)


# TODO should i remove it?
''' def update_droplet(self, centroid, contour, area):

        if compute_euclidean_dist(self.centroid, centroid) > MOVEMENT_TOLERANCE:
            dis = compute_euclidean_dist(self.centroid,centroid)
        if dis > MOVEMENT_TOLERANCE:
            distances[self.dropId] += dis
            self.centroid = centroid
            self.contour = contour
            paths[self.dropId].append(centroid)
            self.modified = True
        if abs(self.area - area) > AREA_TOLERANCE:
            self.area = area
'''

# GLOBAL VARIABLES
global M, iM, count, head, syringes, count, frame, R, ix, iy, evobot, droplets, sockets, syringeToUse, volumeToUse, deepnessToGo

ix = 200
iy = 200
R = 1

paths = defaultdict(list)
distances = defaultdict(list)

dropCount = 0
droplets = []

# SETTINGS
SENSITIVITY_VALUE = 23  # Blurring function parameter
BLUR_SIZE = 14  # Blurring function parameter

MIN_AREA = 10  # Minimum area for droplets to be recognized
MOVEMENT_TOLERANCE = 5  # Limit for updating droplet positi2on
AREA_TOLERANCE = 40  # Limit of area change for updating

DEBUG_MODE = False
RECORDING = False

date = ""
fourCC = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')


def god():
    global M, iM
    print syringeToUse
    M = syringes[syringeToUse].affineMat
    iM = cv2.invertAffineTransform(M)


NAME_TO_SYRINGE_ID = {
    'other': 0,
    'salt': 1,
}

SYRINGE_ID_TO_NAME = {v: k for k, v in NAME_TO_SYRINGE_ID.iteritems()}


def initialize():
    global M, iM, count, head, syringes, frame, evobot, modality, sockets, syringeToUse, volumeToUse, deepnessToGo
    syringes = []
    usrMsgLogger = DataLogger()
    evobot = EvoBot(PORT_NO, usrMsgLogger)
    head = Head(evobot)
    sockets = evobot.getPopulatedSockets()
    syringeToUse = NAME_TO_SYRINGE_ID['other']
    volumeToUse = 0

    for c in sockets:
        syr = Syringe(evobot, {'ID': int(c), 'SYRINGE_LIMIT': -68, 'PLUNGER_LIMIT': 43, 'GOAL_POS': -55,
                               'PLUNGER_CONVERSION_FACTOR': 1})
        # syr.plungerSetConversion(1)
        syr.plungerMoveToDefaultPos()
        syr.syringeMove(0)
        syringes.append(syr)

    head.home()
    god()
    count = 0


def maskFrame(frame, mask):
    global R
    mask.fill(0)
    R = cv2.getTrackbarPos('R', 'Result')
    cv2.circle(mask, (ix, iy), R, (255, 255, 255), -1)
    frame = cv2.bitwise_and(frame, mask)
    return frame


def nothing(x):
    pass


def onClick(event, x, y, flags, param):
    global ix, iy
    if param == "setting":
        if event == cv2.EVENT_RBUTTONUP:
            ix = x
            iy = y
    elif param == "moving":
        if event == cv2.EVENT_RBUTTONUP:  # tasto destro per tirare su
            impixel = np.float32([x, y, 1])
            RobCor = np.dot(M, impixel)
            pullAction(RobCor[0], RobCor[1])
            # threading.Thread(target=pullAction, args=(RobCor[0], RobCor[1])).start()
        elif event == cv2.EVENT_LBUTTONDOWN:  # tasto sinistro per pushare
            impixel = np.float32([x, y, 1])
            RobCor = np.dot(M, impixel)
            pushAction(RobCor[0], RobCor[1], x, y)
            # threading.Thread(target=pushAction, args=(RobCor[0], RobCor[1])).start()
            # (/*-+)


def pullAction(x, y):
    global syringes, head, syringeToUse, deepnessToGo
    head.move(x, y)  # provare a spostare qui per pipeline (/*-+)
    vol = cv2.getTrackbarPos('Volume [ml]', 'Result')
    vol /= 20.0

    if syringes[syringeToUse].canAbsorbVol(vol):
        mov = cv2.getTrackbarPos('Deepness', 'Result')
        syringes[syringeToUse].syringeMove(-mov)
        syringes[syringeToUse].plungerPullVol(vol)
        syringes[syringeToUse].syringeMove(0)
    else:
        print "Volume exceeds capacity"
    print x, y


def pushAction(x, y, mouse_x, mouse_y):
    global other_start_position, salt_position
    if SYRINGE_ID_TO_NAME[syringeToUse] == 'other':
        other_start_position = (mouse_x, mouse_y,)
        print('metto giu la droplet', other_start_position)
    elif SYRINGE_ID_TO_NAME[syringeToUse] == 'salt':
        salt_position = (mouse_x, mouse_y,)
        print('metto giu il sale', salt_position)

    global syringes, head, syringeToUse, deepnessToGo
    head.move(x, y)  # provare a spostare qui per pipeline (/*-+)
    vol = cv2.getTrackbarPos('Volume [ml]', 'Result')
    vol /= 20.0
    if syringes[syringeToUse].canDispenseVol(vol):
        mov = cv2.getTrackbarPos('Deepness', 'Result')
        syringes[syringeToUse].syringeMove(-mov)
        syringes[syringeToUse].plungerPushVol(vol)
        syringes[syringeToUse].syringeMove(0)
    else:
        print "Volume exceeds content"


def getSimilarIndex(drop):
    for c in range(0, len(droplets)):
        distance = floatEuclideanDist(droplets[c].centroid, drop.centroid)
        if distance < 50:
            return c
        else:
            continue
    return -1


def isInTheArray(drop):  # IMPROVABLE
    for drp in droplets:
        distance = floatEuclideanDist(drp.centroid, drop.centroid)
        if distance < 50:
            return True
    return False


def floatEuclideanDist(p, q):
    px = p[0]
    py = p[1]
    qx = q[0]
    qy = q[1]
    diffX = abs(qx - px)
    diffY = abs(qy - py)
    return float(math.sqrt((diffX * diffX) + (diffY * diffY)))


def track(threshImage, result, color):
    global droplets, dropCount
    _, contours, hierarchy = cv2.findContours(threshImage, cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_NONE)  # Finds the contours in the image

    refarea = 0

    if len(contours) > 0:
        dropCount = len(hierarchy)

    for cnt in contours:
        cnt = cv2.convexHull(cnt)
        MOM = cv2.moments(cnt)
        area = MOM['m00']
        if area > 5 and area > refarea:
            min_rect = cv2.fitEllipse(cnt)
            centroid = (min_rect.center.x, min_rect.center.y)
            # centroid = (int(MOM['m10'] / area), int(MOM['m01'] / area))
            refarea = area
            drop = MyDroplet(dropCount, centroid, cnt, color, area)
            cv2.drawContours(result, cnt, -1, (0, 255, 0), 1)
            message = "Color : " + str(color)
            # message2 = "Centroid : " + str(centroid)
            cv2.putText(result, message, centroid, cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            # cv2.putText(result,message2,(centroid[0],centroid[1]+30),cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            # cv2.putText(result,"Total number : " + str(dropCount),(20,20),cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            if len(droplets) == 0 or not isInTheArray(drop):
                print "Added droplet " + str(dropCount)
                droplets.append(drop)
            else:
                index = getSimilarIndex(drop)
                if index == -1:
                    print "ERROR"
                    exit()
                    # droplets[index].updateDroplet(centroid, cnt, area)


def getBiggest():
    max = 0
    for drp in droplets:
        if drp.area > max:
            max = drp.area
            drop = drp
    return drop


def getBlue():
    for drp in droplets:
        if drp.color == "blue":
            drop = drp
    return drop


def removeBiggest(x, y):
    global syringe, head, modality
    head.move(x, y)
    syringe.syringeMove(-65)
    syringe.plungerPullVol(15)  # Adjust for droplets
    syringe.syringeMove(0)
    head.move(0, 0)
    modality = "tracking"


def update(x):
    global syringeToUse, volumeToUse, deepnessToGo
    syringeToUse = cv2.getTrackbarPos('Syringe', 'Result')
    volumeToUse = cv2.getTrackbarPos('Volume [ml]', 'Result')
    deepnessToGo = cv2.getTrackbarPos('Deepness', 'Result')
    god()


def main():
    global R, ix, iy, M, modality, evobot, sockets, syringeToUse, deepnessToGo, volumeToUse, DEBUG_MODE, RECORDING, date, start_tracking_time, end_tracking_time
    cv2.namedWindow('Result')
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(3, WINDOW_SIZE[0])
    cap.set(4, WINDOW_SIZE[1])
    # out = cv2.VideoWriter('C:\Users\Alessandro\Desktop\Experiments\experiment.avi', fourCC, 20.0, (640,480))
    initialize()
    sockets = evobot.getPopulatedSockets()

    modality = "setting"  # it can be "setting", "moving", "tracking"
    old_modality = None

    cv2.createTrackbar('R', 'Result', 0, 500, nothing)  # Create trackbar for masking
    cv2.createTrackbar('Syringe', 'Result', 0, len(sockets) - 1, update)
    cv2.createTrackbar('Deepness', 'Result', 0, 68, nothing)
    cv2.createTrackbar('Volume [ml]', 'Result', 0, 400, update)

    ret, frame = cap.read()
    if ret == 0:
        print "ERROR READING INPUT"

    x, y, z = frame.shape
    mask = np.zeros((x, y, 3), np.uint8)

    while 1:
        ret, frame = cap.read()
        if ret == 0:
            print "ERROR READING INPUT"

        result = frame.copy()
        cv2.circle(result, (ix, iy), R, (0, 0, 255), 2)
        cv2.setMouseCallback('Result', onClick, modality)
        frame = maskFrame(frame, mask)

        # OPTIONS
        key = cv2.waitKey(30) & 0xFF
        if key == 27:
            end_tracking_time = datetime.datetime.now()
            break
        elif key == ord('1'):
            if modality == "setting":
                print "Already in SETTING MODE. Click to set the center and adjust the radius with the trackbar"
            if modality == "moving":
                modality = "setting"
                print "SETTING MODE. Click to set the center and adjust the radius with the trackbar"
            if modality == "tracking":
                modality = "setting"
                print "SETTING MODE. Click to set the center and adjust the radius with the trackbar"
        elif key == ord('2'):
            if modality == "setting":
                modality = "moving"
                print "MOVING MODE. Right Click to pull and Left Click to push"
            if modality == "moving":
                print "Already in MOVING MODE. Right Click to pull and Left Click to push"
            if modality == "tracking":
                modality = "moving"
                print "MOVING MODE. Right Click to pull and Left Click to push"
        elif key == ord('3'):
            if modality == "setting":
                head.move(0, 0)
                modality = "tracking"
                print "TRACKING MODE. C : count droplets"
            if modality == "moving":
                head.move(0, 0)
                modality = "tracking"
                print "TRACKING MODE. C : count droplets"
            if modality == "tracking":
                print "Already in TRACKING MODE. C : count droplets"
        elif key == ord('d'):
            DEBUG_MODE = not DEBUG_MODE
            print "Debug Mode switched"
        elif key == ord('r'):
            RECORDING = not RECORDING
            if RECORDING:
                date = str(datetime.datetime.now())
                import os
                file_name = os.path.join(FILE_PATH, "%s_video" % vt.removeColon(date))
                out = cv2.VideoWriter(file_name, fourCC, 30.0, WINDOW_SIZE)
            else:
                out.release()

        # MODALITIES
        if modality == "setting":
            cv2.circle(result, (ix, iy), 1, (0, 0, 255), 2)
        if modality == "tracking":
            if start_tracking_time is None:
                start_tracking_time = datetime.datetime.now()

            # Image blurring and thresholding
            frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # RED TRACKING
            threshImage = cv2.bitwise_or(cv2.inRange(frameHSV, lower, upper), cv2.inRange(frameHSV, lower2, upper2))
            cv2.blur(threshImage, (5, 5), threshImage)
            cv2.threshold(threshImage, 0, 255, cv2.THRESH_OTSU, threshImage)
            cv2.morphologyEx(threshImage, cv2.MORPH_OPEN, (20, 20), threshImage)
            cv2.morphologyEx(threshImage, cv2.MORPH_CLOSE, (20, 20), threshImage)
            track(threshImage, result, "red")
            # BLUE TRACKING
            # threshImage = cv2.inRange(frameHSV, lower_blue, upper_blue)
            # threshImage = cv2.blur(threshImage, (BLUR_SIZE, BLUR_SIZE))
            # _, threshImage = cv2.threshold(threshImage, SENSITIVITY_VALUE, 255, cv2.THRESH_BINARY)
            # track(threshImage, result, "blue")
            if DEBUG_MODE:
                cv2.imshow('Threshold Image', threshImage)
            else:
                cv2.destroyWindow('Threshold Image')
            if key == ord('c'):
                print "there are " + str(dropCount) + " droplets"

        if modality == "setting":
            cv2.putText(result, "SETTING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
        elif modality == "moving":
            m1 = "Syringe to use : " + str(syringes[syringeToUse].syringeID)
            m2 = "Volume : " + str(float(volumeToUse) / 200.0) + " ml"
            # m3 = "Deepness: " + str(deepnessToGo)
            cv2.putText(result, "MOVING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            cv2.putText(result, m1, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            cv2.putText(result, m2, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            # cv2.putText(result, m3, (10, 68), cv2.FONT_HERSHEY_SIMPLEX, .4, 255)
            if key == ord("w"):
                print "WASHINGGGGGGGGG"
        elif modality == "tracking":
            cv2.putText(result, "TRACKING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)

        if RECORDING:
            out.write(result)
            cv2.putText(result, "RECORDING", (150, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
        cv2.imshow('Result', result)

    print "COMPLETE PATH :"
    for drp in droplets:
        for c in paths[drp.dropId]:
            print c

    print "DISTANCES :"
    for drp in droplets:
        for c in distances[drp.dropId]:
            print c

    for drp in droplets:
        starting_point = paths[drp.dropId][0]
        ending_point = paths[drp.dropId][-1]

        print(other_start_position)
        print(ending_point)

        # other_end_position = (
        #     ending_point[0] * other_start_position[0] / starting_point[0],
        #     ending_point[1] * other_start_position[1] / starting_point[1]
        # )

        print("wawaawawawwawaaw", starting_point, other_start_position)

        for index, c in enumerate(paths[drp.dropId]):
            cv2.circle(result, c, 1, (255, 0, 0), 1)
            if index == 0:
                print('inizio', c)
                cv2.putText(result, "BEGIN", c, cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            elif index == len(paths[drp.dropId]) - 1:
                print('fine', c)
                cv2.putText(result, "END", c, cv2.FONT_HERSHEY_SIMPLEX, .5, 255)

        import csv

        with open('/Users/carlottaporcelli/paths/input-{}.csv'.format(start_tracking_time), 'wb') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([
                'X salt',
                'Y salt',
                'X droplet Start',
                'Y droplet Start',
                'X droplet End',
                'Y droplet End',
                'time',
            ])
            tracking_time = (end_tracking_time - start_tracking_time).total_seconds() * 1000

            if salt_position is None or salt_position is None:
                print "maybe you should put on the petri the ingredients"

            writer.writerow([
                salt_position[0],
                salt_position[1],
                starting_point[0],
                starting_point[1],
                ending_point[0],
                ending_point[1],
                tracking_time,
            ])

        print('----->', starting_point, ending_point, salt_position, tracking_time)

    if RECORDING:
        import os
        file_name = os.path.join(FILE_PATH, "%s_screen.jpg" % vt.removeColon(date))
        cv2.imwrite(file_name, result)
    cv2.imshow("Result", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    evobot.printcore.disconnect()
    exit()


if __name__ == "__main__":
    main()
