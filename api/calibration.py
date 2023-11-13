import numpy as np
from matplotlib import pyplot as plt
from time import sleep
import math
import sys, cv2

sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from petridish import PetriDish
import os


class Calibration:
    def __init__(self, evobot, head, petridish= None, customPoints= None, syringe=None):
        self.evobot = evobot
        self.head = head
        self.petridish = petridish
        self.syringe = syringe
        self.clickNo = 0
        self.frame = None
        self.affineMat = None
        if customPoints is not None:
            self.objPoints = np.float32([customPoints[0], customPoints[1], customPoints[2]])
        elif petridish is not None:
            self.objPoints = np.float32([[0, 0], [0, 0], [0, 0]])
        self.imgPoints = np.float32([[0, 0], [0, 0], [0, 0]])
        self.x = None
        self.y = None

    def calObjPoints(self):
        pointcounter = 0
        if self.petridish is not None:
            Rup = (self.petridish.diameter / 2) + 5
            degrees = [0, 125, 260]
            for degree in degrees:
                self.objPoints[pointcounter, 0] = self.petridish.center[0] + Rup * math.cos(math.radians(degree))
                self.objPoints[pointcounter, 1] = self.petridish.center[1] + Rup * math.sin(math.radians(degree))
                pointcounter += 1

    def affineCalibrate(self):

        self.calObjPoints()
        self.evobot.home()
        self.head.move(self.objPoints[0, 0], self.objPoints[0, 1])
        self.syringe.syringeMove(self.syringe.syringeGoalPos)

        # mouse callback function
        cv2.namedWindow('result')
        cap = cv2.VideoCapture(CAMERA_ID)
        cv2.setMouseCallback('result', self.onMouse)

        while True:
            _, self.frame = cap.read()
            self.frame = cv2.resize(self.frame, IMAGE_SIZE)
            cv2.imshow('result', self.frame)
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def onMouse(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.x = x
            self.y = y
            if self.clickNo == 3:
                self.syringe.syringeMove(0)
                impixel = np.float32([self.x, self.y, 1])
                RobCor = np.dot(self.affineMat, impixel)
                self.head.move(RobCor[0], RobCor[1])

                self.syringe.syringeMove(self.syringe.syringeGoalPos)
            elif self.clickNo < 3:
                self.imgPoints[self.clickNo, 0], self.imgPoints[self.clickNo, 1] = self.x, self.y

                if self.clickNo < 2:
                    self.syringe.syringeMove(0)
                    self.head.move(self.objPoints[self.clickNo + 1, 0], self.objPoints[self.clickNo + 1, 1])
                    self.syringe.syringeMove(self.syringe.syringeGoalPos)

                elif self.clickNo == 2:
                    self.affineMat = cv2.getAffineTransform(self.imgPoints, self.objPoints)
                    self.affineMatInv = cv2.invertAffineTransform(self.affineMat)
                    if not os.path.isdir("affinemat"):
                        os.makedirs("affinemat")
                    np.save('affinemat/' + str(self.syringe.syringeID), self.affineMat)

                self.clickNo += 1
