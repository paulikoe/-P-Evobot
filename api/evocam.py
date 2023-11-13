import sys
import threading
import cv2
import numpy as np
import datetime

sys.path.append('../api')
import math
import time
from configuration import *
from droplet import Droplet


class EvoCam:
    def __init__(self, evobot):

        self.cameraID = CAMERA_ID
        self.frame = None
        self.frameNr = 0
        self.quit = False
        self.time = 0
        self.cap = cv2.VideoCapture(self.cameraID)
        _, img = self.cap.read()
        x, y, z = img.shape
        self.image = img
        self.mask = np.zeros((x, y, 3), np.uint8)
        self.mask.fill(255)

        # this is variables for video saving
        self.height, self.width, layers = img.shape
        self.outputVideo = None
        self.hasWindow = False

        self.droplets = []
        self.trackingThread = None
        self.countingThread = None
        self.evobot = evobot

    def openWindow(self):
        self.hasWindow = True
        self.window = cv2.namedWindow('image')

    def record(self, filename, extension='.mkv'):

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.outputVideo = cv2.VideoWriter('experiments/' + filename + time.strftime("%Y-%m-%d %H%M%S") + extension,
                                           fourcc, 10.0, (self.width, self.height), True)

    def disconnect(self):
        self.quit = True
        if self.trackingThread is not None:
            self.trackingThread.join()
        if self.countingThread is not None:
            self.countingThread.join()
        for droplet in self.droplets:
            droplet.dataLogger.file.close()
        if self.hasWindow:
            cv2.destroyAllWindows()

    def updateWindow(self, *droplets):
        if self.hasWindow:
            _, frame = self.cap.read()
            for droplet in droplets:
                cv2.drawContours(frame, droplet.contour, -1, droplet.contourBGR, 3)
            cv2.imshow('image', frame)
            cv2.waitKey(1)

    def trackDroplet(self, droplet, syringe):
        self.droplets.append(droplet)
        self.trackingThread = threading.Thread(target=self.__trackingThread, args=(droplet, syringe,))
        self.trackingThread.start()

    def __trackingThread(self, droplet, syringe):
        frameNr = 0
        affineTrans = syringe.affineMat
        if affineTrans is None:
            print "TRACKING NOT WORKING - Please run camera calibration"
            self.disconnect()
        affineMat = affineTrans[0:2, 0:2]
        affineDet = abs(np.linalg.det(affineMat))
        while not self.quit:
            _, img = self.cap.read()
            if self.outputVideo is not None:
                self.outputVideo.write(img);

            masked_image = cv2.bitwise_and(img, self.mask)
            # smooth it
            self.frame = cv2.blur(masked_image, (4, 4))

            # convert to hsv and find range of colors
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

            thresh = cv2.inRange(hsv, droplet.lowerhsv, droplet.upperhsv)
            # morphological operators, closing and then opening
            kernel = np.ones((9, 9), np.uint8)
            # st = cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
            thresh_close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            thresh_open = cv2.morphologyEx(thresh_close, cv2.MORPH_OPEN, kernel)
            thresh = thresh_open

            _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # finding contour
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > droplet.minSizeP and area < droplet.maxSizeP:
                    cv2.drawContours(self.frame, cnt, -1, (0, 255, 0), 3)

                    droplet.areaBuf.append(area)
                    if len(droplet.areaBuf) > droplet.areaBufLen:
                        del droplet.areaBuf[0]
                    # the droplet area which is in the range defined
                    area = np.mean(droplet.areaBuf)

                    # finding centroids
                    M = cv2.moments(cnt)
                    xP, yP = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
                    # creating buffer for center to make it unsusceptible to noise by averaging
                    droplet.xPBuf.append(xP)
                    if len(droplet.xPBuf) > droplet.cntBufLen:
                        del droplet.xPBuf[0]
                    xP = int(np.mean(droplet.xPBuf))
                    droplet.yPBuf.append(yP)
                    if len(droplet.yPBuf) > droplet.cntBufLen:
                        del droplet.yPBuf[0]
                    yP = int(np.mean(droplet.yPBuf))

                    timeMs = time.time() - self.evobot.iniTime
                    impixel = np.float32([xP, yP, 1])
                    centerM = np.dot(affineTrans, impixel)
                    xM, yM = round(centerM[0], 2), round(centerM[1], 2)

                    areaM = round(area * affineDet, 2)
                    droplet.setData([frameNr, timeMs, xP, yP, area, xM, yM, round(areaM, 2)])
                    droplet.contour = cnt
                    frameNr += 1

        if self.outputVideo is not None:
            self.outputVideo.release()

    def countBlobs(self, blobs, syringe):
        self.countingThread = threading.Thread(target=self.__countingThread, args=(blobs, syringe,))
        self.countingThread.start()

    def __countingThread(self, blobs, syringe):
        affineTrans = syringe.affineMat
        affineMat = affineTrans[0:2, 0:2]
        affineDet = abs(np.linalg.det(affineMat))
        while not self.quit:
            _, img = self.cap.read()

            masked_image = cv2.bitwise_and(img, self.mask)
            # smooth it
            self.frame = cv2.blur(masked_image, (4, 4))

            # convert to hsv and find range of colors
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

            thresh = cv2.inRange(hsv, blobs.lowerhsv, blobs.upperhsv)
            # morphological operators, closing and then opening
            kernel = np.ones((9, 9), np.uint8)
            # st = cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
            thresh_close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            thresh_open = cv2.morphologyEx(thresh_close, cv2.MORPH_OPEN, kernel)
            thresh = thresh_open

            _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # finding contour
            count = 0
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if blobs.minSizeP < area < blobs.maxSizeP:
                    count += 1
            blobs.count = count
