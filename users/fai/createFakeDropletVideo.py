#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "anfv"
__date__ = "$15-Sep-2016 20:10:39$"

if __name__ == "__main__":
    print "Creating fake video with two droplets";

import numpy as np
import cv2
#import VisionTools as vT
import datetime
import time
import os
import math

height=400
width=400
window_size=(height,width)


fourCC = cv2.VideoWriter_fourcc(*'MJPG')
date = str(datetime.datetime.now())
#file_name = os.path.join("C:/", "%s_video.avi" % vT.removeColon(date))
file_name = "C:/5.avi"
out = cv2.VideoWriter(file_name, fourCC, 10.0, window_size)

pos_x = 350
pos_y = 200
for i in range(1,33):
    img = np.zeros((height,width,3), np.uint8)
    #cv.Circle(img, center, radius, color, thickness=1, lineType=8, shift=0)
    pos_x -= (9 +10*math.sin(i/0.9))
    pos_y -= (9 +10*math.sin(i/0.9))
    cv2.circle(img, (int(pos_x),int(pos_y)), 15, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (300,100+i), 5, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (200,100+i), 8, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (150,120+i), 8, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (250,120+i), 8, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (300,200+i), 9, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (100,200+i), 10, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (150,230+i), 9, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (250,230+i), 9, (0,0,255), thickness=-1, lineType=8, shift=0)
    #cv2.circle(img, (100+i,250-i), 5, (0,0,255), thickness=-1, lineType=8, shift=0)
    cv2.imshow("fakeDropletVideo", img) 
    cv2.waitKey(30)
    out.write(img)

for i in range(1, 10):
    pos_x += 3
    pos_y += 3
    img = np.zeros((height, width, 3), np.uint8)
    cv2.circle(img, (int(pos_x),int(pos_y)), 15, (0, 0, 255), thickness=-1, lineType=8, shift=0)
    cv2.imshow("fakeDropletVideo", img)
    cv2.waitKey(30)
    out.write(img)