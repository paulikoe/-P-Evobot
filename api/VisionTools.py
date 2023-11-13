import cv2, sys
import numpy as np
from matplotlib import pyplot as plt
from time import sleep

sys.path.append('../api')
from evobot import EvoBot
import math


def nothing(x):
    pass


def createTrackbars(windowName, Trackbars):
    for Track in Trackbars:
        cv2.createTrackbar(Track[0], windowName, Track[1], Track[2], nothing)


def getTrackbars(windowname, Trackbars):
    TrackbarVals = {}
    for Track in Trackbars:
        TrackbarVals[Track[0]] = cv2.getTrackbarPos(Track[0], windowname)

    return TrackbarVals


def setText(dst, (x, y), s):
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), lineType=cv2.LINE_AA)


def Distance(u, v):
    distance = np.linalg.norm(np.array(u) - np.array(v))
    return distance


def saveVideo(fileName, (H1, W1)):
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter(fileName + '.avi', fourcc, 16.0, (W1, H1))
    return writer


def removeColon(string):
    colonless = ''
    for char in str(string):
        if char is not ':':
            colonless = colonless + char
    return colonless
