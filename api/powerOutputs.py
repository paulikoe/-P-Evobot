import datetime
import time
import threading
from configuration import *
import datalogger, math


class PowerOutputs:
    """
    This class encapsulated methods for controlling the power outputs (12V) 
    of the robot. (D8, D9 and D10)
    """

    def __init__(self, _evobot):
        """
        This method initializes the pump class. The key parameter is evobot
        to which this head is attached and the x and y limits of the robot
        given in mm.
        """
        self.evobot = _evobot

        # these are only updated upon receiving new positions form robot
        self.d8 = 0
        self.d9 = 0
        self.d10 = 0
        self.pumpConversion = [1, 1, 1]  # ml per mm

        self.dataLogger = None
        self.evobot.heads.append(self)
        self.event = threading.Event()
        self.logBuffer = [0, 0, 0, 0, 0]
        self.logTitlesNeeded = True
        self.timeNow = None
        self.pumpSpeed = 80

    def _recvcb(self, line):
        """
        This is an internal use method that is used to parse messages from the robot
        """

        terms = []
        if line.startswith('M286'):
            terms = str(line).split()
            print terms
            if terms[1].startswith('ON'):
                self.d8 = 1
            if terms[1].startswith('OFF'):
                self.d8 = 0
            if terms[2].startswith('ON'):
                self.d9 = 1
            if terms[2].startswith('OFF'):
                self.d9 = 0
            if terms[3].startswith('ON'):
                self.d10 = 1
            if terms[3].startswith('OFF'):
                self.d10 = 0


            #            if self.dataLogger is not None:
            #                self.timeNow=time.time() - self.evobot.iniTime
            #                eSpeed=(self.eOrg-self.logBuffer[1]) / (self.timeNow-self.logBuffer[0])
            #
            #
            #                try:
            #                    if self.dataLogger.kind=='dat':
            #                        self.dataLogger( str( self.timeNow) + ' ' + str(self.eOrg) + "\n")
            #                    elif self.dataLogger.kind=='csv':
            #                        if self.logTitlesNeeded:
            #                            self.dataLogger(('time', 'eSpeed'))
            #                            self.logTitlesNeeded= False
            #
            #
            #                        self.dataLogger( (str( self.timeNow ), str(self.eOrg) ))
            #                except:
            #                    pass
            #
            #                self.logBuffer=[self.timeNow,self.eOrg]

            self.event.set()

    def _updatePositionFromRobot(self):
        self.evobot.send('M286')
        self.event.wait()
        self.event.clear()

    def turnOnD8(self, t=None):
        """
        This method switches on the D8 output for "t" milliseconds.
        If time is not specified, the output is turned on indefinitely
        The method blocks the caller until the robot has completed
        the time.
        """

        self.evobot._logUsrMsg('D8 is switching on')
        if t is not None:
            moveToMsg = 'M286 D8 V1 T' + str(t)
        else:
            moveToMsg = 'M286 D8 V1'
        self.evobot.send(moveToMsg)
        time.sleep(0.1)
        self._updatePositionFromRobot()
        if t is not None:
            if t > 0:
                while not self.d8 == 0:
                    self._updatePositionFromRobot()
        self.evobot._logUsrMsg('D8 switched on')

    def turnOnD9(self, t=None):
        """
        This method switches on the D9 output for "t" milliseconds.
        If time is not specified, the output is turned on indefinitely
        The method blocks the caller until the robot has completed
        the time.
        """
        self.evobot._logUsrMsg('D9 is switching on')
        if t is not None:
            moveToMsg = 'M286 D9 V1 T' + str(t)
        else:
            moveToMsg = 'M286 D9 V1'
        self.evobot.send(moveToMsg)
        time.sleep(0.1)
        self._updatePositionFromRobot()
        if t is not None:
            if t > 0:
                while not self.d9 == 0:
                    self._updatePositionFromRobot()
        self.evobot._logUsrMsg('D9 switched on')

    def turnOnD10(self, t=None):
        """
        This method switches on the D10 output for "t" milliseconds.
        If time is not specified, the output is turned on indefinitely
        The method blocks the caller until the robot has completed
        the time.
        """
        self.evobot._logUsrMsg('D10 is switching on')
        if t is not None:
            moveToMsg = 'M286 D10 V1 T' + str(t)
        else:
            moveToMsg = 'M286 D10 V1'
        self.evobot.send(moveToMsg)
        time.sleep(0.1)
        self._updatePositionFromRobot()
        if t is not None:
            if t > 0:
                while not self.d10 == 0:
                    self._updatePositionFromRobot()
        self.evobot._logUsrMsg('D10 switched on')

    def turnOffD8(self):
        """
        This method moves the swiches off the D8 output .
        """
        self.evobot._logUsrMsg('D8 is switching off')
        moveToMsg = 'M286 D8 V0'
        self.evobot.send(moveToMsg)
        time.sleep(0.1)
        self._updatePositionFromRobot()
        self.evobot._logUsrMsg('D8 swiched off')

    def turnOffD9(self):
        """
        This method moves the swiches off the D8 output .
        """
        self.evobot._logUsrMsg('D9 is switching off')
        moveToMsg = 'M286 D9 V0'
        self.evobot.send(moveToMsg)
        time.sleep(0.1)
        self._updatePositionFromRobot()
        self.evobot._logUsrMsg('D9 swiched off')

    def turnOffD10(self):
        """
        This method moves the swiches off the D8 output .
        """
        self.evobot._logUsrMsg('D10 is switching off')
        moveToMsg = 'M286 D10 V0'
        self.evobot.send(moveToMsg)
        time.sleep(0.1)
        self._updatePositionFromRobot()
        self.evobot._logUsrMsg('D10 swiched off')

    def home(self):
        # Needed to home the evobot. 
        print "homming power outputs"
        print "hommed power outputs"