import time
import threading
import math
import datetime
import sys
from head import Head
from petridish import PetriDish
from worldcor import WorldCor
from stepperdriver import StepperDriver
import os
import numpy as np
from configuration import *


class Syringe:
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

        self.plungerPos = -1  # mm
        # this is when the plunger is completely push down - corresponding to plungerPos = 0
        self.plungerLimit = syringeConfig['PLUNGER_LIMIT']
        self.plungerConversion = syringeConfig['PLUNGER_CONVERSION_FACTOR']  # ml per mm

        self.syringeSpeed = 0
        self.syringeAcc = 0
        self.plungerSpeed = 0
        self.plungerAcc = 0

        self.syringeStatus = StepperDriver()
        self.plungerStatus = StepperDriver()

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
        terms = []
        if line.startswith('I'):
            terms = str(line).split()
            if self.syringeID == int(terms[1]):
                self.syringePos = round(float(terms[3]), 1)
                self.plungerPos = round(float(terms[5]), 2)
                self.event.set()
                if self.dataLogger is not None:
                    timeNow = time.time() - self.evobot.iniTime
                    sSpeed = (self.syringePos - self.logBuffer[1]) / (timeNow - self.logBuffer[0])
                    pSpeed = (self.plungerPos - self.logBuffer[2]) / (timeNow - self.logBuffer[0])
                    sAcceleration = (sSpeed - self.logBuffer[3]) / (timeNow - self.logBuffer[0])
                    pAcceleration = (pSpeed - self.logBuffer[4]) / (timeNow - self.logBuffer[0])
                    try:
                        if self.dataLogger.kind == 'dat':
                            self.dataLogger(
                                str(time.time() - self.evobot.iniTime) + ' ' + str(self.syringePos) + ' ' + str(
                                    self.plungerPos) + "\n")
                        elif self.dataLogger.kind == 'csv':
                            if self.logTitlesNeeded:
                                self.dataLogger((
                                    'time', 'syringePos', 'plungerPos', 'sSpeed', 'pSpeed', 'sAcceleration',
                                    'pAcceleration'))
                                self.logTitlesNeeded = False

                            self.dataLogger((str(timeNow), str(self.syringePos), str(self.plungerPos), str(sSpeed),
                                             str(pSpeed), str(sAcceleration), str(pAcceleration)))
                    except:
                        pass
                    self.logBuffer = [timeNow, self.syringePos, self.plungerPos, sSpeed, pSpeed]
        if line.startswith('SYRINGE_STATUS'):
            terms = str(line).split()
            if ('I' == terms[1]):
                if self.syringeID == int(terms[2]):
                    if 'S' == terms[3]:
                        try:
                            self.syringeStatus.updateStatus(int(terms[4]))
                        except Exception as e:
                            print (e)
                    else:
                        if 'P' == terms[3]:
                            try:
                                self.plungerStatus.updateStatus(int(terms[4]))
                            except Exception as e:
                                print (e)

                    if 'S' == terms[5]:
                        self.syringeStatus.updateStatus(int(terms[6]))
                    else:
                        if 'P' == terms[5]:
                            self.plungerStatus.updateStatus(int(terms[6]))
                        #                try:
                        #                    eS, msgS = self.syringeStatus.analyseStatus()
                        #                    eP, msgP = self.plungerStatus.analyseStatus()
                        #                    print "Status syringe " + str(self.syringeID) + ", syringe= " + msgS + ",
                            # plunger= " + msgP
                        #                except Exception as e:
                        #                    print e

    def _getPos(self):
        """
        Private method that is internally used in the class to obtain
        the positions of both the syringe and the plunger.
        """

        syringeGetPosMsg = 'M290 I' + str(self.syringeID)
        self.evobot.send(syringeGetPosMsg)
        if not self.event.wait(1.0):
            print ("No message received before timeout when requesting syringe position")
        self.event.clear()

    def plungerGetPos(self):
        """
        This method returns the position of the plunger in mm.
        """

        # self._getPos()
        return self.plungerPos

    def syringeGetPos(self):
        """
        This method returns the position of the syringe in mm.
        """

        # self._getPos()
        return self.syringePos

    def syringeGetSpeed(self):
        """
        This method returns the syringe speed
        """
        return self.syringeSpeed

    def syringeGetAcc(self):
        """
        This method returns the syringe acceleration
        """
        return self.syringeAcc

    def plungerGetSpeed(self):
        """
        This method returns the plunger speed
        """
        return self.plungerSpeed

    def plungerGetAcc(self):
        """
        This method returns the plunger acceleration
        """
        return self.plungerAcc

    def plungerSetConversion(self, factor):  # mm per ml
        """
        This is method used for calibrating the plunger.
        It sets the mm per ml of the plunger
        """

        self.plungerConversion = factor

    def plungerGetConversion(self):
        """
        This method returns the current mm per ml convertion factor of the
        plunger motor.
        """
        return self.plungerConversion

    def plungerSetSpeed(self, goalSpeed):  # steps/s
        """
        Method that sets the maximum speed of the movement of the plunger.
        """
        if goalSpeed < 3 or goalSpeed > 288:
            self.evobot._logUsrMsg('Plunger attempted to set its maximum speed to ' + str(
                goalSpeed) + 'steps/s, but exceed plunger ' + str(
                self.syringeID) + 'speed\'s limits of [3:288] (0.125:12 turns/s)')
            self.evobot.quit()

        goalSpeed = round(goalSpeed, 0)

        self.evobot._logUsrMsg('Setting plunger maximum speed to ' + str(goalSpeed) + 'steps/s')
        plungerSetSpeedMsg = 'M295 I' + str(self.syringeID) + ' P' + str(goalSpeed)
        self.evobot.send(plungerSetSpeedMsg)
        self.plungerSpeed = goalSpeed
        self.evobot._logUsrMsg('Plunger speed set')

    def plungerSetAcc(self, goalAcc):  # steps/s
        """
        Method that sets the acceleration of the movement of the plunger.
        """
        if goalAcc < 3 or goalAcc > 96:
            self.evobot._logUsrMsg(
                'Plunger attempted to set its acceleration to ' + str(goalAcc) + 'steps/s2, but exceed plunger ' + str(
                    self.syringeID) + 'acceleration\'s limits of [3:96] (0.125:4 turns/s2)')
            self.evobot.quit()

        goalAcc = round(goalAcc, 0)

        self.evobot._logUsrMsg('Setting plunger maximum acceleration to ' + str(goalAcc) + 'steps/s')
        plungerSetAccMsg = 'M296 I' + str(self.syringeID) + ' P' + str(goalAcc)
        self.evobot.send(plungerSetAccMsg)
        self.plungerAcc = goalAcc
        self.evobot._logUsrMsg('Plunger acceleration set')

    def syringeSetSpeed(self, goalSpeed):  # steps/s
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

    def syringeSetAcc(self, goalAcc):  # steps/s
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

    def syringeMove(self, goalPos):  # mm
        """
        This move the syringe mm. This is a blocking call, hence, control
        is not returned to the caller until the syringe has finished moving.
        """

        if goalPos > 0 or goalPos < self.syringeLimit:
            self.evobot._logUsrMsg('Syringe attempt to move past limits of [0:' + str(self.syringeLimit) + ']')
            return
            # self.evobot.quit()

        goalPos = round(goalPos, 1)

        self.evobot._logUsrMsg('Syringe moving to ' + str(goalPos) + 'mm (absolute)')

        syringeMoveMsg = 'M290 I' + str(self.syringeID) + ' S' + str(goalPos)
        self.evobot.send(syringeMoveMsg)
        now = datetime.datetime.now()
        while not self.syringeGetPos() == goalPos:
            self._getPos()
            time_delta = (datetime.datetime.now() - now)

            if time_delta > datetime.timedelta(seconds=60):
                self.evobot._logUsrMsg("Timeout when moving the syringe.")
                self.evobot._logUsrMsg("Goal pos: " + str(goalPos) + " Syringe pos: " + str(self.syringeGetPos()))
                syringeStatusMsg = 'M289 I' + str(self.syringeID)
                self.evobot.send(syringeStatusMsg)
                time.sleep(2)
                self.evobot._logUsrMsg("Trying to move the syringe again...")
                self.evobot.send(syringeMoveMsg)
                now = datetime.datetime.now()

        self.evobot._logUsrMsg('Syringe moved')

    def plungerMovePos(self, goalPos):  # mm
        """
        Method that controls the movement of the plunger in mm.
        """
        goalPos = round(goalPos, 2)

        if goalPos < 0 or goalPos > self.plungerLimit:
            self.evobot._logUsrMsg('Plunger attempted to move to ' + str(goalPos) + 'mm, but exceed plunger ' + str(
                self.syringeID) + '\'s limits of [0:' + str(self.plungerLimit) + ']')
            self.evobot.quit()

        self.evobot._logUsrMsg('Plunger moving to ' + str(goalPos) + 'mm (absolute)')
        plungerMoveMsg = 'M290 I' + str(self.syringeID) + ' P' + str(goalPos)
        self.evobot.send(plungerMoveMsg)

        while not self.plungerGetPos() == round(float(goalPos), 2):
            self._getPos()
        self.evobot._logUsrMsg('Plunger moved')

    def plungerExtrude(self):
        """
        Method that controls the extruding of the plunger.
        """
        goalPos = self.plungerLimit

        self.evobot._logUsrMsg('Plunger extruding to ' + str(goalPos) + 'mm (absolute)')
        plungerMoveMsg = 'M290 I' + str(self.syringeID) + ' P' + str(goalPos)
        self.evobot.send(plungerMoveMsg)

    def plungerPullVol(self, ml):
        """
        This method pulls ml of liquid.
        """

        self.evobot._logUsrMsg('Plunger pulling ' + str(ml))
        self.plungerMovePos(self.plungerPos - ml * self.plungerConversion)
        self.evobot._logUsrMsg('Plunger pulled')

    def continuous_dispensation_of_liquid(self, head, petridish_center, liquid_volume, radius, radius_max):
        """This function pulls liquid rotating on itself inside the limits of the petridish.
           Move the head in circles until the syringe is empty - move up syringe in the end
           Parameters:
               radius = 15
               radius_max = 30
               petridish_center = center of the petridish were to dispense the liquid
               head = head of the robot
               liquid_volume = volume of the liquid to be dispensed
        """
        self.evobot._logUsrMsg('Pouring liquid continuously with the syringe ' + str(self.syringeID))

        increasing = True
        start_pos = self.plungerGetPos()
        print ('this is the starting position: ' + str(start_pos))

        lala = round(start_pos + liquid_volume * self.plungerConversion, 2)
        print ('this is the distance to move: ' + str(lala))

        self.plungerPushVolNonBlocking(liquid_volume)
        self.radius = radius

        while self.plungerGetPos() != lala:
            for itr in range(1, 45):
                if increasing:
                    radius += float(float(radius_max) / 45) * 2
                else:
                    radius -= float(float(radius_max) / 45) * 2
                if radius > radius_max:
                    increasing = False
                if radius < 0:
                    increasing = True

                angle = (float(itr) / float(45)) * float(8 * math.pi)
                x_pos = round(petridish_center[0] + radius * math.cos(angle), 1)
                y_pos = round(petridish_center[1] + radius * math.sin(angle), 1)
                if x_pos < 0:
                    x_pos = 0
                if x_pos > HEAD['X_LIMIT']:
                    x_pos = HEAD['X_LIMIT']
                if y_pos < 0:
                    y_pos = 0
                if y_pos > HEAD['Y_LIMIT']:
                    y_pos = HEAD['Y_LIMIT']
            head.moveContinously(x_pos, y_pos)
            self._getPos()

    def mixing_up_liquids_(self, head, x, y, volume_to_mix, air_volume, syringe_height, rounds):
        """ This function mix up a volume of liquid in the center of the dedicated petridish.
            Parameters:
                head = head of the robot
                petridish = element petridish of PetriDish class where the mixture is
                volume_to_mix = amount of liquid to mix up
                syringe_height = syringe position to reach the liquid
                rounds = number of times the mixing has to be done
        """

        head.move(x, y)
        self.plungerPullVol(air_volume)
        self.syringeMove(syringe_height)
        count = 0
        while count < rounds:
            # cycle to mix volume
            self.plungerPullVol(volume_to_mix)
            self.plungerPushVol(volume_to_mix)
            count += 1
        self.plungerMoveToDefaultPos()
        self.homeSyringe()

    def plungerPushVol(self, ml):
        """
        This method pushes ml of liquid.
        """

        self.evobot._logUsrMsg('Plunger pushing ' + str(ml))
        self.plungerMovePos(self.plungerPos + ml * self.plungerConversion)
        self.evobot._logUsrMsg('Plunger pushed')

    def plungerPushVolNonBlocking(self, ml):
        """This method pushes ml of liquid."""

        self.evobot._logUsrMsg('Plunger pushing ' + str(ml) + "(non blocking)")
        self.plungerMovePosNonBlocking(self.plungerPos + ml * self.plungerConversion)
        self.evobot._logUsrMsg('Plunger pushed' + "(non blocking)")

    def plungerMovePosNonBlocking(self, goalPos):  # mm
        """
        Method that controls the movement of the plunger.
        """
        goalPos = round(goalPos, 2)
        print (goalPos)
        if goalPos < 0 or goalPos > self.plungerLimit:
            self.evobot._logUsrMsg('Plunger attempted to move to ' + str(goalPos) + ' mm, but exceed syringe\'s ' + str(
                self.syringeID) + ' plunger limits of [0:' + str(self.plungerLimit) + ']')
            self.evobot.quit()

        self.evobot._logUsrMsg('Plunger moving to ' + str(goalPos) + 'mm (absolute) (non blocking)')
        plungerMoveMsg = 'M290 I' + str(self.syringeID) + ' P' + str(goalPos)
        self.evobot.send(plungerMoveMsg)

        self.evobot._logUsrMsg('Plunger moved (non blocking)')

    def plungerMoveVol(self, ml):
        """
        This method is convenience function that pulls ml of liquid
        if ml is negative and pushes ml liquid if ml is positive.
        """
        if (ml < 0):
            self.plungerPullVol(-ml)
        else:
            self.plungerPushVol(ml)

    def plungerMoveToDefaultPos(self):
        """
        This a helper method that moves the plunger to its limit.
        In other words, prepare the syringe for pulling liquid.
        """

        self.evobot._logUsrMsg('Plunger moving to ' + str(self.plungerLimit))
        self.plungerMovePos(self.plungerLimit - 0.1)
        self.evobot._logUsrMsg('Plunger moved')

    def home(self):
        """
        This homes the syringe and the plunger by moving them to their
        upper most position where the homing switches are activated.
        """

        self.evobot._logUsrMsg('homing syringe (plunger and syringe)' + str(self.syringeID))
        self.evobot.send('M291 I' + str(self.syringeID))
        while not self.syringeGetPos() == 0:
            self._getPos()
        if not self.plungerPos == 0:
            self._getPos()
        self.evobot._logUsrMsg('homed syringe')

    def homeSyringe(self):
        """
        This homes the syringe by moving it to its
        upper most position where the homing switch is activated.
        """

        self.evobot._logUsrMsg('homing syringe (syringe only, not plunger)' + str(self.syringeID))
        homeSyringeMsg = 'M291 I' + str(self.syringeID) + " S"
        self.evobot.send(homeSyringeMsg)
        now = datetime.datetime.now()
        while not self.syringeGetPos() == 0:
            self._getPos()
            # time_delta = datetime.datetime.now() - now
            # print time_delta
            # if time_delta > datetime.timedelta(seconds=60):
            #     self.evobot._logUsrMsg("Timeout when homing the syringe.")
            #     self.evobot._logUsrMsg("Goal pos: " + str(0) + " Syringe pos: " + str(self.syringeGetPos()))
            #     syringeStatusMsg = 'M289 I' + str(self.syringeID)
            #     self.evobot.send(syringeStatusMsg)
            #     time.sleep(2)
            #     self.evobot._logUsrMsg("Trying to home the syringe again...")
            #     self.evobot.send(homeSyringeMsg)
            #     now = datetime.datetime.now()

        self.evobot._logUsrMsg('homed syringe')

    def homePlunger(self):
        """
        This homes the plunger by moving it to its
        upper most position where the homing switch is activated.
        """

        self.evobot._logUsrMsg('homing plunger ' + str(self.syringeID))
        self.evobot.send('M291 I' + str(self.syringeID) + " P")
        while not self.plungerGetPos() == 0:
            self._getPos()
        self.evobot._logUsrMsg('homed plunger')

    def park(self):
        self.syringeMove(self.syringeLimit)

    def fillVolFrom(self, head, ml, container):
        center = container.worldCor.worldCorFor(container.center, self.syringeID)
        if ml is 'all':
            ml = self.plungerPos
        self.syringeMove(container.goalPos + container.edgeHeight)
        head.move(center[0], center[1])
        self.syringeMove(container.goalPos)
        self.plungerPullVol(ml)
        self.syringeMove(container.goalPos + container.edgeHeight)

    def emptyVolTo(self, head, ml, container):
        center = container.worldCor.worldCorFor(container.center, self.syringeID)
        if ml is 'all':
            ml = self.plungerLimit - self.plungerPos
        self.syringeMove(container.goalPos + container.edgeHeight)
        head.move(center[0], center[1])
        self.syringeMove(container.goalPos)
        self.plungerPushVol(ml)
        self.syringeMove(container.goalPos + container.edgeHeight)

    def syringe_wash(self, head, container_waste, container_clean, times=3, volume_clean_liquid=5):
        """This function empty the syringe in the container_waste, pulls clean liquid (water) from the 
        container_clean and repeats the operations the number of times
        Parameters:
           container_clean and container_waste are PetriDish objects 
        """

        center_waste = container_waste.worldCor.worldCorFor(container_waste.center, self.syringeID)
        center_clean = container_clean.worldCor.worldCorFor(container_clean.center, self.syringeID)

        self.homeSyringe()
        self.plungerMoveToDefaultPos()

        for count in xrange(0, times):
            print ('THIS is the %d time' % count)
            self.homeSyringe()
            head.move(center_clean[0], center_clean[1])
            self.syringeMove(self.syringeLimit)
            self.plungerPullVol(volume_clean_liquid)
            self.homeSyringe()
            head.move(center_waste[0], center_waste[1])  # move head to waste container
            self.syringeMove(-20)
            self.plungerPushVol(volume_clean_liquid)
        self.homeSyringe()

    def goToXY(self, head, point, worldcor):

        mm = worldcor.worldCorFor((point[0], point[1]), self.syringeID)
        head.move(round(float(mm[0]), 1), round(float(mm[1]), 1))

    def isEmpty(self):
        if round(float(self.plungerPos), 2) >= round(float(self.plungerLimit), 2):
            return True
        else:
            return False

    def isFull(self):
        if round(float(self.plungerPos), 2) == 0:
            return True
        else:
            return False

    def canDispenseVol(self, vol):
        if round(float(self.plungerLimit), 2) - round(float(self.plungerPos), 2) >= round(float(vol), 2):
            return True
        else:
            return False

    def canAbsorbVol(self, vol):
        if round(float(self.plungerPos), 2) >= round(float(vol), 2):
            return True
        else:
            return False

    def getXY(self, head, worldcor):
        mm = worldcor.inverseWorldCorFor((head.getX(), head.getY()), self.syringeID)
        return (round(float(mm[0]), 1), round(float(mm[1]), 1))

    def plungerHardStop(self):
        self.evobot._logUsrMsg('stopping (hard) the plunger ' + str(self.syringeID))
        self.evobot.send('M293 I' + str(self.syringeID) + " P")
        time.sleep(0.1)
        self._getPos()
        self.evobot._logUsrMsg('stopped plunger')

    def plungerSoftStop(self):
        self.evobot._logUsrMsg('stopping (soft) the plunger ' + str(self.syringeID))
        self.evobot.send('M294 I' + str(self.syringeID) + " P")
        time.sleep(0.3)
        self._getPos()
        self.evobot._logUsrMsg('stopped plunger')

    def syringeHardStop(self):
        self.evobot._logUsrMsg('stopping (hard) the syringe ' + str(self.syringeID))
        self.evobot.send('M293 I' + str(self.syringeID) + " S")
        time.sleep(0.1)
        self._getPos()
        self.evobot._logUsrMsg('stopped syringe')

    def syringeSoftStop(self):
        self.evobot._logUsrMsg('stopping (soft) the syringe ' + str(self.syringeID))
        self.evobot.send('M294 I' + str(self.syringeID) + " S")
        time.sleep(0.3)
        self._getPos()
        self.evobot._logUsrMsg('stopped syringe')
