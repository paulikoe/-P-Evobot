#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "anfv"
__date__ = "$15-Sep-2016 21:33:34$"

if __name__ == "__main__":
    print "test tracking";

import numpy as np
import cv2
import VisionTools as vT
import datetime
import time
import os
import sys
sys.path.append('../../settings')
sys.path.append('../../api')
from configuration import *
from multiDropletTracking import MultiDropletTracking
from evobot import EvoBot
from syringe import Syringe
from datalogger import DataLogger
from worldcor import WorldCor
import math

fourCC = cv2.VideoWriter_fourcc(*'XVID')
height=400
width=400
window_size=(height,width)

salt_position = (145, 3)  # salt position on petridish
decanol_position = (103, 120)  # decanol position on petridish

"""variables for red circle used to delineate the area of the experiment"""
ix = 200
iy = 200
R = 120


def trasform_matrixes():
    global decanol_matrix, decanol_matrix_transformed, salt_matrix, salt_matrix_transformed
    decanol_matrix = decanol_syringe.affineMat
    decanol_matrix_transformed = cv2.invertAffineTransform(decanol_matrix)
    salt_matrix = salt_syringe.affineMat
    salt_matrix_transformed = cv2.invertAffineTransform(salt_matrix)

def maskFrame(frame, mask):
    global R
    mask.fill(0)
    cv2.circle(mask, (ix, iy), R, (255, 255, 255), -1)
    frame = cv2.bitwise_and(frame, mask)
    return frame



def perform_experiment(number):
    cv2.namedWindow('Schermata')
    cap = cv2.VideoCapture('C:/fakeDropletsVideo'+ number + '.avi')
    cap.set(3, 400)
    cap.set(4, 400)
    ret, frame = cap.read()
    if ret == 0:
        print 'ERROR READING INPUT'

    x, y, z = frame.shape
    mask = np.zeros((x, y, 3), np.uint8)

    start_tracking_time = None

    

    
    modality = "tracking"
    print "TRACKING MODE. C : count droplets"
    # We start an exp!!!
    recording = True
    if recording:
        date = str(datetime.datetime.now())
        import os
        file_name = os.path.join("C:/", "%s_video.avi" % vT.removeColon(date))
        out = cv2.VideoWriter(file_name, fourCC, 10.0, window_size)
#        else:
#            out.release()
    start_tracking_time = datetime.datetime.now()
    
    track2 = MultiDropletTracking(decanol_matrix)
    while True:
        ret, frame = cap.read() ###Read a new frame
        if ret == 0:
            print "ERROR READING INPUT"
            break
        result = frame.copy()
        cv2.circle(result, (ix, iy), R, (0, 0, 255), 2)
        # cv2.setMouseCallback('Schermata', self.onClick, param=modality)
        frame = maskFrame(frame, mask)

        # OPTIONS
        # Waits up to other 30ms for a keypress
        # If none -> -1
        key = cv2.waitKey(500) & 0xFF

        now = datetime.datetime.now()
        done_tracking = modality == "tracking" and ((start_tracking_time + datetime.timedelta(seconds=40)) <= now)

        if done_tracking:
            print "Stop", done_tracking, start_tracking_time, now
            end_tracking_time = now
            break
        elif key == ord('q'):
            print "Aborted", done_tracking, start_tracking_time, now
            end_tracking_time = now
            break




        # MODALITA'
        if modality == "setting":
            cv2.putText(result, "SETTING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            cv2.circle(result, (ix, iy), R, (0, 0, 255), 2)
        elif modality == "moving":
            cv2.putText(result, "MOVING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
        elif modality == "tracking":
            cv2.putText(result, "TRACKING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            track2.do_track(frame, result)

        if recording:
            out.write(result)
            cv2.putText(result, "RECORDING", (150, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
        cv2.imshow('Schermata', result)
#            cv2.waitKey(30)
        
    #END WHILE TRUE
    # cv2.waitKey(int(start_tracking_time + datetime.timedelta(seconds=10)))

    _, ending_point = track2.show_output_biggest(result)
    point= np.float32([ending_point[0], ending_point[1], 1])
    RobCor = np.dot(decanol_matrix, point)
    ending_point=(RobCor[0], RobCor[1])
    print "Coordinates of the end point of the droplet (mm): " + str(ending_point)
    
    print "Coordinates of the initial position of the decanol: " + str(decanol_position)
    print "original salt pos: " + str(salt_position)
    saltPosInDecanolCS=worldcor.inverseWorldCorFor(salt_position, salt_syringe)
    print "Coordinates of the salt pos in the Decanol Coordinate System (mm): " + str(saltPosInDecanolCS)
    
    if recording:
        import os
        file_name = os.path.join("C:/", "%s_screen.jpg" % vT.removeColon(date))
        cv2.imwrite(file_name, result)
        out.release()
    cv2.imshow("Schermata", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # exit()

    import csv
    with open('input-{}.csv'.format(start_tracking_time.strftime("%Y-%m-%d %H.%M.%S")), 'wb') as f:
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
        tracking_time = (end_tracking_time - start_tracking_time).total_seconds()

        if salt_position is None or salt_position is None:
            print "maybe you should put on the petri the ingredients"

        writer.writerow([
            salt_position[0],
            salt_position[1],
            decanol_position[0],
            decanol_position[1],
            ending_point[0],
            ending_point[1],
            tracking_time,
        ])
    print('----->', decanol_position, ending_point, salt_position, tracking_time)

    def _calculate_pitagora(a, b):
        return math.sqrt(a ** 2 + b ** 2)

    fitness_value = (_calculate_pitagora(ending_point[0] - saltPosInDecanolCS[0], ending_point[1] - saltPosInDecanolCS[1])) \
                        / (_calculate_pitagora(decanol_position[0] - ending_point[0],
                                               decanol_position[1] - ending_point[1]))

    print fitness_value
    return fitness_value


usrmsglogger = DataLogger()
evobot = EvoBot(PORT_NO, usrmsglogger)
decanol_syringe = Syringe(evobot, SYRINGE0)
salt_syringe = Syringe(evobot, SYRINGE1)
worldcor=WorldCor(decanol_syringe, mode='default')

trasform_matrixes()
perform_experiment("5")
perform_experiment("6")
perform_experiment("7")