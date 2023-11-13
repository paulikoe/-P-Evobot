import datetime
import time
import threading
from configuration import *
import datalogger, math
from stepperdriver import StepperDriver


class Servo:
    """
    This class encapsulated methods for controlling the servo of the robot
    """

    def __init__(self, _evobot, servoConfig):
        """
        This method initializes the servo class. The key parameter is evobot
        to which this servo is attached
        """

        self.servoPin = servoConfig['SERVO_PIN']  # P0, P1 or P2
        self.servoLimit = servoConfig['SERVO_LIMIT']  # 180 grades
        self.goal_pos = servoConfig['SERVO_GOAL_POS']
        self.home_pos = servoConfig['SERVO_ZERO_POS']
        self.evobot = _evobot

        # these are only updated upon receiving new positions from robot
        self.e = -1
        self.eOrg = -1  # Original e, before rounding

        if self.servoPin == 0:
            self.evobot._logUsrMsg('Init servo P0')
        else:
            if self.servoPin == 1:
                self.evobot._logUsrMsg('Init servo P1')
            else:
                if self.servoPin == 2:
                    self.evobot._logUsrMsg('Init servo P2')
                else:
                    print ""
                    self.evobot._logUsrMsg('Error: The servo pin is not correct: ' + self.servoPin)
                    self.evobot.quit()

        self.servo_status = StepperDriver() # TODO: is it needed?
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
        if line.startswith('P'):
            terms = str(line).split()
            self.servoPin = terms[1][1:]
            if terms[2].startswith('S'):
                self.goal_pos = terms[2][1:]
            self.event.set()

    def setDataLogger(self, logger):
        """
        This sets the data logger for the head. The data consist
        of the time, x, and y positions of the robot. The argument
        is a function that takes a string as input.
        """
        self.dataLogger = logger

    def servoMove(self, goal_position):
        """
        This method moves the head to the position (x,y) specified in mm.
        The method blocks the caller until the robot has completed
        the movement.
        """

        if goal_position < 0 or goal_position > self.servoLimit:
            self.evobot._logUsrMsg('Servo attempt to move past limits of [0:' + str(self.servoLimit) + ']')
            return

        # Choose the correct Pin to use
        if self.servoPin == 0:
            self.evobot.send('P0')
        elif self.servoPin == 1:
            self.evobot.send('P1')
        else:
            self.evobot.send('P2')

        self.evobot._logUsrMsg('Servo moving to pos ' + str(goal_position))

        if self.servoPin == 0 or self.servoPin == 1 or self.servoPin == 2:
            moveToMsg = 'M280 P%d S%f' % (self.servoPin, goal_position)
        print moveToMsg
        self.evobot.send(moveToMsg)
        self.evobot._logUsrMsg('Servo moved')

    def servo_home(self):
        # Choose the correct Pin to use
        if self.servoPin == 0:
            self.evobot.send('P0')
        elif self.servoPin == 1:
            self.evobot.send('P1')
        else:
            self.evobot.send('P2')

        if self.servoPin == 0 or self.servoPin == 1 or self.servoPin == 2:
            moveToMsg = 'M280 P%d S%f' % (self.servoPin, self.home_pos)
        print moveToMsg
        self.evobot.send(moveToMsg)
        self.evobot._logUsrMsg('Servo homed')

