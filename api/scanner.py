import time
import threading
import datetime
import sys
from head import Head
from petridish import PetriDish
from worldcor import WorldCor
import os
import numpy as np


class Scanner:
    def __init__(self, _evobot, scannerConfig):
        """
        This method initialize the scanner object. The parameters
        are the evobot object to which this scanner is attached.
        The scanner configuration vector which incudes the ID of 
        this scanner object and the its movement limits 
        """
        self.scannerID = scannerConfig['ID']
        self.evobot = _evobot

        if not str(self.scannerID) in self.evobot.populatedSockets:
            self.evobot._logUsrMsg('Scanner initialization failed: no scanner on socket ' + str(self.scannerID))
            self.evobot._logUsrMsg('Available sockets: ' + str(self.evobot.populatedSockets))
            self.evobot.quit()
            return

        self.scannerPos = -1  # mm
        self.scannerLimit = scannerConfig['SCANNER_LIMIT']  # this is when the scanner is completely push down
        self.dateLogger = None
        self.evobot.modules.append(self)
        self.event = threading.Event()
        self.logBuffer = [0, 0, 0, 0, 0]
        self.logTitlesNeeded = True
        fname = '../calibration/affinemat/' + str(self.scannerID) + '.npy'
        if os.path.isfile(fname):
            self.affineMat = np.load(fname)
        else:
            self.affineMat = None

    def _recvcb(self, line):
        """
        Private methods that handles messages received from the robot
        """

        terms = []
        if line.startswith('I'):
            terms = str(line).split()
            if (self.scannerID == int(terms[1])):
                self.scannerPos = round(float(terms[3]), 2)
                self.event.set()
                if self.dataLogger is not None:
                    timeNow = time.time() - self.evobot.iniTime
                    sSpeed = (self.scannerPos - self.logBuffer[1]) / (timeNow - self.logBuffer[0])
                    sAcceleration = (sSpeed - self.logBuffer[2]) / (timeNow - self.logBuffer[0])
                    try:
                        if self.dataLogger.kind == 'dat':
                            self.dataLogger(str(time.time() - self.evobot.iniTime) + ' ' + str(self.scannerPos) + "\n")
                        elif self.dataLogger.kind == 'csv':
                            if self.logTitlesNeeded:
                                self.dataLogger(('time', 'scannerPos', 'sSpeed', 'sAcceleration'))
                                self.logTitlesNeeded = False

                            self.dataLogger((str(timeNow), str(self.scannerPos), str(sSpeed), str(sAcceleration)))
                    except:
                        pass
                    self.logBuffer = [timeNow, self.scannerPos, sSpeed]

    def _getPos(self):
        """
        Private method that is internally used in the class to obtain
        the positions of the sscanner.
        """

        scannerGetPosMsg = 'M290 I' + str(self.scannerID)
        self.evobot.send(scannerGetPosMsg)
        self.event.wait()
        self.event.clear()

    def scannerGetPos(self):
        """
        This method returns the position of the scanner in mm.
        """

        self._getPos()
        return self.scannerPos

    def setDataLogger(self, logger):
        """
        This sets the data logger for the head. The data logged consist
        of the time and scanner position. The argument
        is a function that takes a string as input.
        """

        self.dataLogger = logger

    def scannerMovePos(self, goalPos):  # mm
        """
        Method that controls the movement of the scanner.
        """
        if goalPos < 0 or goalPos > self.scannerLimit:
            self.evobot._logUsrMsg('Scanner attempted to move to ' + str(goalPos) + 'mm, but exceed scanner ' + str(
                self.scannerID) + '\'s limits of [0:' + str(self.scannerLimit) + ']')
            self.evobot.quit()

        goalPos = round(goalPos, 2)

        self.evobot._logUsrMsg('Scanner moving to ' + str(goalPos) + 'mm')
        scannerMoveMsg = 'M290 I' + str(self.scannerID) + ' P' + str(goalPos)
        self.evobot.send(scannerMoveMsg)

        while not self.scannerGetPos() == round(float(goalPos), 2):
            pass
        self.evobot._logUsrMsg('Scanner moved')

    def scannerRise(self, mm):
        """
        This method rises mm millimeters the scanner .
        """

        self.evobot._logUsrMsg('Scanner rising ' + str(mm) + 'mm')
        self.scannerMovePos(self.scannerPos - mm)
        self.evobot._logUsrMsg('Scanner rised')

    def scannerDescend(self, mm):
        """
        This method descends mm millimeters the scanner .
        """

        self.evobot._logUsrMsg('Scanner descending ' + str(mm) + 'mm')
        self.scannerMovePos(self.scannerPos + mm)
        self.evobot._logUsrMsg('Scanner descended')

    def scannerMoveRel(self, mm):
        """
        This method is convenience function that descends mm millimiters 
        if mm is negative and rises mm millimeters if mm is positive.
        """
        if mm < 0:
            self.scannerDescend(-mm)
        else:
            self.scannerRise(mm)

    def home(self):
        """
        This homes the scaner by moving it to its
        upper most position where the homing switch is activated.
        """

        self.evobot._logUsrMsg('homing scanner ' + str(self.scannerID))
        self.evobot.send('M291 I' + str(self.scannerID))
        while not self.scannerGetPos() == 0:
            pass

        self.evobot._logUsrMsg('homed scanner')

    def park(self):
        self.scannerMovePos(0)

    def goToXY(self, head, point, worldcor):
        # TODO: This is not working well (the scanner module is different from
        # a syringe in the same socket), we must fix it 

        mm = worldcor.worldCorFor((point[0], point[1]), self.scannerID)
        head.move(round(float(mm[0]), 2), round(float(mm[1]), 2))

    def getXY(self, head, worldcor):
        # TODO: This is not working well (the scanner module is different from
        # a syringe in the same socket), we must fix it 

        mm = worldcor.inverseWorldCorFor((head.getX(), head.getY()), self.scannerID)
        return round(float(mm[0]), 2), round(float(mm[1]), 2)
