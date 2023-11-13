import os
import threading
import time

import numpy as np

from configuration import *


class Dispenser:
    def __init__(self, _evobot, syringeConfig):
        """
        This method initialize the syringe object. The parameters
        are the evobot object to which this syringe is attached.
        The ID of this syringe object and the movement limits of
        the syringe and the plunger in mm
        """
        self.syringeID = syringeConfig['ID']
        self.syringeGoalPos = syringeConfig['GOAL_POS']
        self.evobot = _evobot

        if not str(self.syringeID) in self.evobot.populatedSockets:
            self.evobot._logUsrMsg('Syringe initialization failed: no syringe on socket ' + str(self.syringeID))
            self.evobot._logUsrMsg('Available sockets: ' + str(self.evobot.populatedSockets))
            self.evobot.quit()
            return

        self.syringePos = -1  # mm
        self.syringeLimit = syringeConfig['SYRINGE_LIMIT']  # mm

        self.syringeSpeed = 0
        self.syringeAcc = 0

        self.dataLogger = None
        self.evobot.modules.append(self)
        self.event = threading.Event()
        self.logBuffer = [0, 0, 0, 0, 0]
        self.logTitlesNeeded = True
        fname = '../calibration/affinemat/' + str(self.syringeID) + '.npy'
        if os.path.isfile(fname):
            self.affineMat = np.load(fname)
        else:
            try:
                # does a exist in the current namespace
                fname = EVOBLISS_SOFTWARE_PATH + 'calibration/affinemat/' + str(self.syringeID) + '.npy'
                if os.path.isfile(fname):
                    self.affineMat = np.load(fname)
                else:
                    self.affineMat = None
            except NameError:
                self.affineMat = None

    def _recvcb(self, line):
        """
        Private methods that handles messages received from the robot
        """
        try:
            terms = []
            if line.startswith('I'):
                terms = str(line).split()
                if self.syringeID == int(terms[1]):
                    pos = terms[3].split('o')[0]
                    self.syringePos = round(float(pos), 1)
                    self.event.set()
                    if self.dataLogger is not None:
                        timeNow = time.time() - self.evobot.iniTime
                        sSpeed = (self.syringePos - self.logBuffer[1]) / (timeNow - self.logBuffer[0])
                        sAcceleration = (sSpeed - self.logBuffer[3]) / (timeNow - self.logBuffer[0])
                        try:
                            if self.dataLogger.kind == 'dat':
                                self.dataLogger(
                                    str(time.time() - self.evobot.iniTime) + ' ' + str(self.syringePos) + "\n")
                            elif self.dataLogger.kind == 'csv':
                                if self.logTitlesNeeded:
                                    self.dataLogger((
                                        'time', 'syringePos', 'sSpeed', 'sAcceleration'))
                                    self.logTitlesNeeded = False

                                self.dataLogger((str(timeNow), str(self.syringePos), str(sSpeed),
                                                 str(sAcceleration)))
                        except:
                            pass
                        self.logBuffer = [timeNow, self.syringePos, sSpeed]
        except Exception as e:
            print e

    def _get_positions(self):
        """
        Private method that is internally used in the class to obtain
        the positions of both the syringe and the plunger.
        """
        syringeGetPosMsg = 'M290 I' + str(self.syringeID)
        self.evobot.send(syringeGetPosMsg)
        if not self.event.wait(1.0):
            print "No message received before timeout when requesting syringe position"
        self.event.clear()

    def dispenser_get_pos(self):
        """
        This method returns the position of the syringe in mm.
        """

        # self._get_positions()
        return self.syringePos

    def dispenser_get_speed(self):
        """
        This method returns the syringe speed
        """
        return self.syringeSpeed

    def dispenser_get_acc(self):
        """
        This method returns the syringe acceleration
        """
        return self.syringeAcc

    def dispenser_set_speed(self, goalSpeed):  # steps/s
        """
        Method that sets the maximum speed of the movement of the syringe.
        """
        if goalSpeed < 50 or goalSpeed > 1500:
            self.evobot._logUsrMsg('Syringe attempted to set its maximum speed to ' + str(
                goalSpeed) + 'steps/s, but exceed syringe ' + str(
                self.syringeID) + 'speed\'s limits of [50:1500] (0.25:7.5 turns/s)')
            self.evobot.quit()

        goalSpeed = round(goalSpeed, 0)

        self.evobot._logUsrMsg('Setting syringe maximum speed to ' + str(goalSpeed) + 'steps/s')
        syringeSetSpeedMsg = 'M295 I' + str(self.syringeID) + ' S' + str(goalSpeed)
        self.evobot.send(syringeSetSpeedMsg)
        self.syringeSpeed = goalSpeed
        self.evobot._logUsrMsg('Syringe speed set')

    def dispenser_set_acc(self, goalAcc):  # steps/s
        """
        Method that sets the acceleration of the movement of the syringe.
        """
        if goalAcc < 50 or goalAcc > 1500:
            self.evobot._logUsrMsg(
                'Syringe attempted to set its acceleration to ' + str(goalAcc) + 'steps/s2, but exceed syringe ' + str(
                    self.syringeID) + 'acceleration\'s limits of [50:1500] (0.25:7.5 turns/s2)')
            self.evobot.quit()

        goalAcc = round(goalAcc, 0)

        self.evobot._logUsrMsg('Setting syringe maximum acceleration to ' + str(goalAcc) + 'steps/s')
        syringeSetAccMsg = 'M296 I' + str(self.syringeID) + ' S' + str(goalAcc)
        self.evobot.send(syringeSetAccMsg)
        self.syringeAcc = goalAcc
        self.evobot._logUsrMsg('Syringe acceleration set')

    def setDataLogger(self, logger):
        """
        This sets the data logger for the head. The data logged consist
        of the time, plunger position, and syringe position. The argument
        is a function that takes a string as input.
        """

        self.dataLogger = logger

    def dispenser_move(self, goalPos):  # mm
        """
        This move the syringe mm. This is a blocking call, hence, control
        is not returned to the caller until the syringe has finished moving.
        """
        # uncomment this line for limits of water pump
        # if goalPos > 0 or goalPos < self.syringeLimit:
        if goalPos > 0 or goalPos < self.syringeLimit:
            self.evobot._logUsrMsg('Syringe attempt to move past limits of [0:' + str(self.syringeLimit) + ']')
            return
            # self.evobot.quit()

        goalPos = round(goalPos, 1)

        self.evobot._logUsrMsg('Syringe moving to ' + str(goalPos) + 'mm (absolute)')

        syringeMoveMsg = 'M290 I' + str(self.syringeID) + ' S' + str(goalPos)
        self.evobot.send(syringeMoveMsg)
        while not self.dispenser_get_pos() == goalPos:
            self._get_positions()
        self.evobot._logUsrMsg('Syringe moved')

    def home(self):
        """
        This homes the syringe and the plunger by moving them to their
        upper most position where the homing switches are activated.
        """
        self.home_dispenser()

    def home_dispenser(self):
        """
        This homes the syringe by moving it to its
        upper most position where the homing switch is activated.
        """

        self.evobot._logUsrMsg('homing syringe ' + str(self.syringeID))
        self.evobot.send('M291 I' + str(self.syringeID) + " S")
        while not self.dispenser_get_pos() == 0:
            self._get_positions()
        self.evobot._logUsrMsg('homed syringe')

    def park(self):
        self.dispenser_move(self.syringeLimit)

    def goToXY(self, head, point, worldcor):

        mm = worldcor.worldCorFor((point[0], point[1]), self.syringeID)
        head.move(round(float(mm[0]), 1), round(float(mm[1]), 1))

    def getXY(self, head, worldcor):
        mm = worldcor.inverseWorldCorFor((head.getX(), head.getY()), self.syringeID)
        return (round(float(mm[0]), 1), round(float(mm[1]), 1))

    def syringeHardStop(self):
        self.evobot._logUsrMsg('stopping (hard) the syringe ' + str(self.syringeID))
        self.evobot.send('M293 I' + str(self.syringeID) + " S")
        time.sleep(0.1)
        self._get_positions()
        self.evobot._logUsrMsg('stopped syringe')

    def syringeSoftStop(self):
        self.evobot._logUsrMsg('stopping (soft) the syringe ' + str(self.syringeID))
        self.evobot.send('M294 I' + str(self.syringeID) + " S")
        time.sleep(0.3)
        self._get_positions()
        self.evobot._logUsrMsg('stopped syringe')
