import numpy as np
import cv2
import math, time
from datalogger import DataLogger
import webcolors


class Droplet:
    def __init__(self, color=None, lowerhsv=None, upperhsv=None, minSizemm=None, maxSizemm=None,
                 minSizePix=None, maxSizePix=None, dataLoggerName=None, contourColor=None):

        self.lowerhsv = np.array(lowerhsv)
        self.upperhsv = np.array(upperhsv)
        self.__setHSV(color)
        self.minSizeM = minSizemm
        self.maxSizeM = maxSizemm
        self.minSizeP = minSizePix
        self.maxSizeP = maxSizePix
        self.xP = None
        self.yP = None
        self.xM = None
        self.yM = None
        self.areaP = None
        self.areaM = None
        self.frameNr = None
        self.time = None
        self.velocityM = None
        self.velocityP = None
        self.data = None
        self.dataBuf = []
        if dataLoggerName is not None:
            fileName = dataLoggerName + time.strftime("%Y-%m-%d %H%M%S")
            self.dataLogger = DataLogger('experiments/' + fileName, kind='csv')
        else:
            self.dataLogger = None
        self.bufLen = 10000
        self.logTitlesNeeded = True
        self.contour = None
        self.contourBGR = self.__colorName2BGR(contourColor)
        # buffers which hold the average of area and center for noise removal
        self.areaBuf = []
        self.areaBufLen = 100
        self.xPBuf, self.yPBuf = [], []
        self.cntBufLen = 3
        self.count = 0

    def __setHSV(self, color):
        if color is None:
            return
        if color == 'default red':
            self.lowerhsv = np.array([140, 40, 40])
            self.upperhsv = np.array([180, 255, 255])

        if color == 'default blue':
            self.lowerhsv = np.array([60, 50, 50])
            self.upperhsv = np.array([160, 255, 255])

    def __setdataLogger(self, data):

        if self.logTitlesNeeded:
            self.dataLogger(('frame number', 'time(ms)', 'centerX(pixels)', 'centerY(pixels)', 'Area(pixels)',
                             'Speed(PixperFrame)', 'centerX(mm)', 'centerY(mm)', 'Area(mm2)', 'Speed(mmps)'))
            self.logTitlesNeeded = False
        self.dataLogger((str(self.data[0]), str(self.data[1]), str(self.data[2]), str(self.data[3]), str(self.data[4]),
                         str(self.data[5]), str(self.data[6]), str(self.data[7]), str(self.data[8]), str(self.data[9])))

    def __colorName2BGR(self, colorName):

        colorRGB = webcolors.name_to_rgb(colorName)
        colorBGR = (colorRGB[2], colorRGB[1], colorRGB[0])
        return colorBGR

    def setData(self, data):

        self.frameNr = data[0]
        self.time = data[1]

        self.xP = data[2]
        self.yP = data[3]
        self.areaP = data[4]

        self.xM = data[5]
        self.yM = data[6]
        self.areaM = data[7]

        if self.frameNr == 0:
            self.velocityP = 0
            self.velocityM = 0

        elif self.frameNr > 0:
            self.velocityP = self.Distance((self.xP, self.yP), self.dataBuf[0][2:4])
            self.velocityM = self.Distance((self.xM, self.yM), self.dataBuf[0][6:8]) / (self.time - self.dataBuf[0][1])

        data.insert(5, self.velocityP)
        data.append(self.velocityM)

        self.data = data
        if self.dataLogger is not None:
            self.__setdataLogger(self.data)

        if len(self.dataBuf) < self.bufLen:
            self.dataBuf.insert(0, data)

        else:
            dataBufCopy = self.dataBuf
            dataBufCopy.insert(0, data)
            del dataBufCopy[self.bufLen]
            self.dataBuf = dataBufCopy

    def Distance(self, u, v):
        distance = np.linalg.norm(np.array(u) - np.array(v))
        return distance

    def angel(u, v):
        vector = np.array(u) - np.array(v)
        theta = math.atan(vector[1] / vector[0])
        distance = np.linalg.norm(np.array(u) - np.array(v))
        return distance

    def getVelocityMM(self):
        return self.velocityM

    def getVelocityPix(self):
        return self.velocityP

    def getPosMM(self):
        return (self.xM, self.yM)

    def getPosPix(self):
        return (self.xP, self.yP)

    def getPosPix(self):
        return (self.xP, self.yP)

    def getData(self):
        return self.dataBuf[0]

    def getContour(self):
        return self.contour

    def isSpeedBelow(self, threshmmps=None, threshpixpfr=None, time=None):
        result = True
        bufLen = len(self.dataBuf)
        if self.dataBuf[0][1] - self.dataBuf[bufLen - 1][1] < time:
            result = False

        if threshmmps is not None:
            for data in self.dataBuf:
                if self.dataBuf[0][1] - data[1] > time:
                    break
                elif data[9] > threshpixpfr:
                    result = False
                    break

        if threshpixpfr is not None:
            for data in self.dataBuf:
                if self.dataBuf[0][1] - data[1] > time:
                    break
                elif data[5] > threshpixpfr:
                    result = False
                    break
        return result

    def isSpeedOver(self, threshmmps=None, threshpixpfr=None, time=None):
        result = True
        bufLen = len(self.dataBuf)
        if self.dataBuf[0][1] - self.dataBuf[bufLen - 1][1] < time:
            result = False

        if threshmmps is not None:
            for data in self.dataBuf:
                if self.dataBuf[0][1] - data[1] > time:
                    break
                elif data[9] < threshpixpfr:
                    result = False
                    break

        if threshpixpfr is not None:
            for data in self.dataBuf:
                if self.dataBuf[0][1] - data[1] > time:
                    break
                elif data[5] < threshpixpfr:
                    result = False
                    break
        return result

    def isStatic(self, threshmmps, threshpixpfr):
        result = True
        if threshmmps is not None:
            if self.velocityM > threshmmps:
                result = False

            if threshpixpfr is not None:
                if self.velocityP > threshpixpfr:
                    result = False
        return result

    def isMobile(self, threshmmps, threshpixpfr):
        result = True
        if threshmmps is not None:
            if self.velocityM < threshmmps:
                result = False

            if threshpixpfr is not None:
                if self.velocityP < threshpixpfr:
                    result = False
        return result

    def countBlobs(self):

        return self.count
