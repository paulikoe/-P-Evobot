import cv2, sys
import numpy as np
from time import sleep

sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
import threading
import VisionTools as vt
from datalogger import DataLogger
from syringe import Syringe
from head import Head
import time
from wellplate import WellPlate
from petridish import PetriDish
from worldcor import WorldCor


class Droplet3dPrinter:
    def __init__(self, evobot, head, syringe, worldcor):
        self.evobot = evobot
        self.head = head
        self.syringe = syringe
        self.worldcor = worldcor
        self.dataLogger = None

    def makeBubble(self, (printPointX, printPointY), (x, y)):
        self.syringe.goToXY(self.head, (printPointX - x, printPointY + y), self.worldcor)
        # time.sleep(1)
        self.syringe.syringeMove(self.goalPos)
        # time.sleep(1)
        self.syringe.plungerPushVol(self.dispenseVol)
        if self.dataLogger is not None and self.head.dataLogger is not None:
            self.dataLogger((str(self.head.timeNow), str(self.head.xOrg), str(self.head.yOrg)))
        time.sleep(1)
        # self.syringe.goToXY(self.head, (printPointX+x+5, printPointY+y), self.worldcor )
        self.syringe.syringeMove(self.upPos)
        # time.sleep(1)

    def count_letters(self, word):
        BAD_LETTERS = " "
        return len([letter for letter in word if letter not in BAD_LETTERS])

    def startPrint(self, printString, printPoint, dimensions=(40, 160), minDistancemm=3, dispenseVol=1, goalPos=None,
                   upPos=None):

        self.dispenseVol = dispenseVol
        self.goalPos = goalPos
        self.upPos = upPos
        printPointX, printPointY = printPoint[0], printPoint[1]
        heightmm, widthmm = dimensions[0], dimensions[1]
        i, j = 0, 0
        points = []
        ratio = heightmm / 40
        blank_img = np.zeros((40 * ratio, 20 * ratio * self.count_letters(printString), 3), np.uint8)
        cv2.putText(blank_img, printString, (20, 20 * ratio), cv2.FONT_HERSHEY_SIMPLEX, ratio * .5, (255, 255, 255), 1)
        gray = cv2.cvtColor(blank_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        for row in gray:
            for colon in row:
                if j == w:
                    j = 0
                if colon == 255:
                    points.append([i, j])

                j += 1
            i += 1

        sampled = []
        wanted = True
        for point1 in points:
            for point2 in sampled:
                if vt.Distance(point1, point2) < minDistancemm:
                    wanted = False
            if wanted is True:
                sampled.append(point1)
            wanted = True

        sampled_img = np.zeros((h, w), np.uint8)
        printed_img = np.zeros((h, w), np.uint8)
        for po in sampled:
            sampled_img[po[0], po[1]] = 255
        cv2.imshow('sampled Text', sampled_img)

        for po2 in sampled:
            self.makeBubble((printPointX, printPointY), (po2[0], po2[1]))
            printed_img[po2[0], po2[1]] = 255
            cv2.imshow('printed Bubbles', printed_img)
            cv2.waitKey(1)
