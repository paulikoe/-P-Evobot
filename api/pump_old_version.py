import datetime
import time
import threading
from configuration import *
import datalogger, math

# this version is the one 'supporting' multiple pumps which has not been tested !!! NOT BEEN TESTED !!!

class Pump:
    """
    This class encapsulated methods for controlling the pump of the robot
    """

    def __init__(self, _evobot, pumpConfig):
        """
        This method initializes the pump class. The key parameter is evobot
        to which this head is attached and the x and y limits of the robot
        given in mm.
        """
        self.evobot = _evobot

        # these are only updated upon receiving new positions from robot
        self.e = -1
        self.eOrg = -1  # Original e, before rounding
        self.pumpConversion = pumpConfig['PUMP_CONVERSION_FACTOR']  # ml per mm
        self.pumpSpeed = 80

        self.pumpSocket = pumpConfig['PUMP_SOCKET']  # Y, E0 or E1
        if self.pumpSocket == 'Y':
            self.evobot._logUsrMsg('Init pump Y')
        else:
            if self.pumpSocket == 'E0':
                self.evobot._logUsrMsg('Init pump E0')
            else:
                if self.pumpSocket == 'E1':
                    self.evobot._logUsrMsg('Init pump E1')
                else:
                    print ""
                    self.evobot._logUsrMsg('Error: The pump socket is not correct: ' + self.pumpSocket)
                    self.evobot.quit()

        self.x = -1
        self.y = -1
        self.xOrg = -1  # Original x, before rounding
        self.yOrg = -1  # Original y, before rounding
        self.ySocket = -1
        self.ySocketOrg = -1
        self.xLimit = HEAD['X_LIMIT']
        self.yLimit = HEAD['Y_LIMIT']
        self.headSpeed = 4000
        self.headSpeedAndPump = 800

        self.dataLogger = None
        self.evobot.heads.append(self)
        self.event = threading.Event()
        self.logBuffer = [0, 0, 0, 0, 0]
        self.logTitlesNeeded = True
        self.timeNow = None

    def _recvcb(self, line):
        """
        This is an internal use method that is used to parse messages from the robot
        """
        terms = []
        if line.startswith('X'):
            terms = str(line).split()
            self.xOrg = float(terms[6][0:])
            self.x = round(self.xOrg, 1)
            if terms[7].startswith('Y'):
                self.ySocketOrg = float(terms[7][2:])
                self.ySocket = round(self.ySocketOrgOrg, 1)
            if terms[8].startswith('Z'):
                self.yOrg = float(terms[8][2:])
                self.y = round(self.yOrg, 1)
            if terms[9].startswith('E'):
                self.eOrg = float(terms[9][2:])
                self.e = round(self.eOrg, 1)
            self.newPositionAvailable = True
            if self.dataLogger is not None:
                self.timeNow = time.time() - self.evobot.iniTime
                eSpeed = (self.eOrg - self.logBuffer[1]) / (self.timeNow - self.logBuffer[0])
                xSpeed = (self.xOrg - self.logBuffer[1]) / (self.timeNow - self.logBuffer[0])
                ySpeed = (self.yOrg - self.logBuffer[2]) / (self.timeNow - self.logBuffer[0])
                distance = math.sqrt(
                    math.pow((self.xOrg - self.logBuffer[1]), 2) + math.pow((self.yOrg - self.logBuffer[2]), 2))
                speed = distance / (self.timeNow - self.logBuffer[0])
                acceleration = math.sqrt(
                    math.pow((xSpeed - self.logBuffer[3]), 2) + math.pow((ySpeed - self.logBuffer[4]), 2)) / (
                                       self.timeNow - self.logBuffer[0])
                try:
                    if self.dataLogger.kind == 'dat':
                        self.dataLogger(str(self.timeNow) + ' ' + str(self.xOrg) + ' ' + str(self.yOrg) + ' ' + str(
                            self.eOrg) + "\n")
                    elif self.dataLogger.kind == 'csv':
                        if self.logTitlesNeeded:
                            self.dataLogger(
                                ('time', 'x', 'y', 'xSpeed', 'ySpeed', 'distance', 'speed', 'acceleration', 'eSpeed'))
                            self.logTitlesNeeded = False

                        self.dataLogger((str(self.timeNow), str(self.xOrg), str(self.yOrg), str(xSpeed), str(ySpeed),
                                         str(distance), str(speed), str(acceleration), str(self.eOrg)))
                except:
                    pass

                self.logBuffer = [self.timeNow, self.xOrg, self.yOrg, xSpeed, ySpeed, self.eOrg]

            self.event.set()

    def _updatePositionFromRobot(self):
        # Choose the correct extruder to use
        if self.pumpSocket == 'E1':
            self.evobot.send('T1')
        else:
            self.evobot.send('T0')
        self.evobot.send('M114')
        self.event.wait()
        self.event.clear()

        # Set the extruder 0 as default
        self.evobot.send('T0')

    def setDataLogger(self, logger):
        """
        This sets the data logger for the head. The data consist
        of the time, x, and y postions of the robot. The argument
        is a function that takes a string as input.
        """
        self.dataLogger = logger

    def pumpMovePos(self, e):
        """
        This method moves the head to the position (x,y) specified in mm.
        The method blocks the caller until the robot has completed
        the movement.
        """

        e = round(e, 1)
        # self.evobot._logUsrMsg( 'pump moving to: ' + str( e ) )

        # Choose the correct extruder to use
        if self.pumpSocket == 'E1':
            self.evobot.send('T1')
        else:
            self.evobot.send('T0')

        if self.pumpSocket == 'E0' or self.pumpSocket == 'E1':
            moveToMsg = 'G1 E%f F%f' % (e, self.pumpSpeed)
        else:
            moveToMsg = 'G1 Y%f F%f' % (e, self.pumpSpeed)
        print moveToMsg
        self.evobot.send(moveToMsg)
        self._updatePositionFromRobot()

        if self.pumpSocket == 'Y':
            while not e == self.ySocket:
                self._updatePositionFromRobot()
        else:
            while not e == self.e:
                self._updatePositionFromRobot()
                # self.evobot._logUsrMsg( 'pump moved')

    def getPumpPos(self):
        """
        This returns the current  position of the pump
        """
        if self.pumpSocket == 'Y':
            return self.ySocket
        else:
            return self.e

    def getE(self):
        """
        This returns the current x position of the robot
        """
        return self.e

    def pumpSetConversion(self, factor):  # mm per ml
        """
        This is method used for calibrating the pump.
        It sets the mm per ml of the plunger
        """

        self.pumpConversion = factor

    def pumpGetConversion(self):
        """
        This method returns the current mm per ml convertion factor of the
        pump motor.
        """
        return self.pumpConversion

    def pumpPullVol(self, ml):
        """
        This method pulls ml of liquid.
        """
        self._updatePositionFromRobot()
        self.evobot._logUsrMsg('Pump pulling ' + str(ml))
        self.pumpMovePos(self.getPumpPos() - ml * self.pumpConversion)
        self.evobot._logUsrMsg('Pump pulled')

    def pumpPushVol(self, ml):
        """
        This method pushes ml of liquid.
        """
        self._updatePositionFromRobot()
        print('got in')
        self.evobot._logUsrMsg('Pump pushing ' + str(ml))
        print('got in')
        self.pumpMovePos(self.getPumpPos() + ml * self.pumpConversion)
        self.evobot._logUsrMsg('Pump pushed')

    def pumpMoveVol(self, ml):
        """
        This method is convenience function that pulls ml of liquid
        if ml is negative and pushes ml liquid if ml is positive.
        """
        if (ml < 0):
            self.pumpPullVol(-ml)
        else:
            self.pumpPushVol(ml)

    def setSpeed(self, goalSpeed):
        """
        This method sets the speed of the pump of the robot
        """
        if goalSpeed < 1 or goalSpeed > 200:
            self.evobot._logUsrMsg('Pump attempted to set its maximum speed to ' + str(
                goalSpeed) + 'mm/min, but exceed pump speed\'s limits of [1:100]')
            self.evobot.quit()

        goalSpeed = round(goalSpeed, 0)

        self.evobot._logUsrMsg('Setting pump maximum speed to ' + str(goalSpeed) + 'mm/min')
        self.pumpSpeed = goalSpeed

        self.evobot._logUsrMsg('Pump speed set')

    def _moveToCenter(self, x, y):
        """
        This method moves the head to the position (x,y) specified in mm.
        The method blocks the caller until the robot has completed
        the movement.
        """

        if x < 0 or x > self.xLimit or y < 0 or y > self.yLimit:
            self.evobot._logUsrMsg('(pump) head movements out of limits ' + str(x) + ", " + str(y))
            self.evobot.quit()

        x = round(x, 1)
        y = round(y, 1)

        self.evobot._logUsrMsg('(pump) moving head to: ' + str(x) + ' ' + str(y) + '...')

        moveToMsg = 'G1 X%f Z%f F%f' % (x, y, self.headSpeed)
        print moveToMsg
        self.evobot.send(moveToMsg)
        self._updatePositionFromRobot()
        while not (x == self.x and y == self.y):
            self._updatePositionFromRobot()
        self.evobot._logUsrMsg('pump) head moved')

    def _move(self, x, y, e, speed):
        """
        This method moves the head to the position (x,y) specified in mm and
        the pump to the position e.
        The method blocks the caller until the robot has completed
        the movement.
        """

        if x < 0 or x > self.xLimit or y < 0 or y > self.yLimit:
            self.evobot._logUsrMsg('(pump) head movements out of limits ' + str(x) + ", " + str(y))
            self.evobot.quit()

        x = round(x, 1)
        y = round(y, 1)
        e = round(e, 1)

        self.evobot._logUsrMsg('pumping and moving head to: ' + str(x) + ' ' + str(y) + ' ' + str(e) + '...')

        moveToMsg = 'G1 X%f Z%f E%f F%f' % (x, y, e, speed)
        # print moveToMsg
        self.evobot.send(moveToMsg)
        self._updatePositionFromRobot()
        while not (x == self.x and y == self.y and e == self.e):
            # print "x: " + str(x) + "x2: " + str(self.x)
            # print "y: " + str(y) + "y2: " + str(self.y)
            # print "e: " + str(e) + "e2: " + str(self.e)
            self._updatePositionFromRobot()
        self.evobot._logUsrMsg('pump and head moved')

    def calculate_speed(self, x, y, e):
        """This function calculates the speed of the movement to be fast and feasible
            for the pump and the head
            Parameters:
                x, y, e: mm of displacement of that movement
        """
        # This seems to work ok, the pump speed is too slow
        return self.headSpeedAndPump

        steps_x = abs(x * 80)
        steps_y = abs(y * 80)
        steps_e = abs(e * 5 * 113)
        # print "steps_x: " + str(steps_x)
        # print "steps_y: " + str(steps_y)
        # print "steps_e: " + str(steps_e)
        max_steps = max(steps_x, steps_y, steps_e)

        # Test with normal head speed
        time = max_steps / float(self.headSpeed)
        speed_e = steps_e / time
        if speed_e < self.pumpSpeed:
            print "The head speed is valid"
            return self.headSpeed
        print "not using head speed, pump speed would be: " + str(speed_e)

        time = steps_e / self.pumpSpeed
        steps_xy = max(steps_x, steps_y)
        speed_xy = steps_xy / time
        if speed_xy < self.headSpeed:
            print "The pump speed is valid"
            return self.pumpSpeed

        print "No valid speed found"
        return self.pumpSpeed

    def continuous_dispensation_of_liquid(self, petridish_center, liquid_volume, radius_max):
        """This function pulls liquid rotating on itself inside the limits of the petridish.
           Move the head in circles until the volume has been dispensed
           Parameters:
               radius_max = 20
               petridish_center = center of the petridish were to dispense the liquid
               liquid_volume = volume of the liquid to be dispensed
        """
        self.evobot._logUsrMsg('pouring liquid continuously with the pump ')
        self._moveToCenter(petridish_center[0], petridish_center[1])
        e_ini = self.e
        increasing = True
        turns = 3
        segments = 8
        radius_min = 25
        radius = radius_min
        for t in range(turns):
            for itr in range(segments):
                if increasing:
                    radius += float(float(radius_max) / segments) * 2
                else:
                    radius -= float(float(radius_max) / segments) * 2
                if radius > radius_max:
                    increasing = False
                    radius = radius_max
                if radius < radius_min:
                    increasing = True
                    radius = radius_min

                angle = (float(itr) / float(segments)) * float(2 * math.pi)
                x_pos = round(petridish_center[0] + radius * math.cos(angle), 1)
                y_pos = round(petridish_center[1] + radius * math.sin(angle), 1)
                if x_pos < 0:
                    x_pos = 0
                if x_pos > self.xLimit:
                    x_pos = self.xLimit
                if y_pos < 0:
                    y_pos = 0
                if y_pos > self.yLimit:
                    y_pos = self.yLimit
                e_pos = self.e + self.pumpConversion * (liquid_volume / float(turns) / float(segments))
                speed = self.calculate_speed(x_pos - self.x, y_pos - self.y, e_pos - self.e)
                self._move(x_pos, y_pos, e_pos, speed)
        print "dispensed " + str((self.e - e_ini) / self.pumpConversion) + "ml"
