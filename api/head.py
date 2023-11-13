import datetime
import time
import threading
from configuration import *
import datalogger, math


class Head:
    """
    This class encapsulated methods for controlling the head of the robot
    """

    def __init__(self, _evobot):
        """
        This method initializes the head class. The key parameter is evobot
        to which this head is attached and the x and y limits of the robot
        given in mm.
        """
        self.evobot = _evobot

        # these are only updated upon receiving new positions form robot
        self.x = -1
        self.y = -1
        self.z = -1
        self.e0 = -1
        self.e1 = -1
        self.xOrg = -1  # Original x, before rounding
        self.yOrg = -1  # Original y, before rounding
        self.zOrg = -1  # Original z, before rounding
        self.e0Org = -1  # Original e0, before rounding
        self.e1Org = -1  # Original e1, before rounding
        
        self.xLimit = HEAD['X_LIMIT']
        self.yLimit = HEAD['Y_LIMIT']
        
        # X_LIMIT and Y_LIMIT are mandatory, the rest are optional
        try: 
            self.zLimit = HEAD['Z_LIMIT']
        except:
            self.zLimit = 0
        try:     
            self.e0Limit = HEAD['E0_LIMIT']
        except:
            self.e0Limit = 0
        try: 
            self.e1Limit = HEAD['E1_LIMIT']
        except:
            self.e1Limit = 0
            
        self.headSpeed = 4000

        self.dataLogger = None
        self.evobot.heads.append(self)
        self.event = threading.Event()
        self.logBuffer = [0, 0, 0, 0, 0] #uchovává pozice hlavy robota
        self.logTitlesNeeded = True
        self.timeNow = None

    def _recvcb(self, line):
        """
        This is an internal use method that is used to parse messages from the robot
        """

        terms = [] #seznam
        if line.startswith('X'): #kontrola, zda zprava obsahuje info o poloze hlavy robota
            terms = str(line).split()
            self.xOrg = float(terms[6][0:]) #vybere sedmy prvek v seznamu terms- převede prvek na číslo
            #s desetinnou čárkou --> původně nezaokrouhledá pozice na na ose X
            self.x = round(self.xOrg, 1) #a zaokrouhlí se
            if terms[7].startswith('Y'):
                self.zOrg = float(terms[7][2:])
                self.z = round(self.zOrg, 1)
            if terms[8].startswith('Z'):
                self.yOrg = float(terms[8][2:])
                self.y = round(self.yOrg, 1)
            if terms[9].startswith('E'): #ovladani pozice pipety???
                self.e0Org = float(terms[9][2:])
                self.e0 = round(self.e0Org, 1)
                
#            # The E1 position is not given using Gcode M114, TODO: Get E1 position
#            if terms[10].startswith('E'):
#                self.e1Org = float(terms[9][2:])
#                self.e1 = round(self.e1Org, 1)
            
            self.newPositionAvailable = True #k dispozici nova pozice
            if self.dataLogger is not None:
                self.timeNow = time.time() - self.evobot.iniTime #časový rozdíl od začátku programu
                xSpeed = (self.xOrg - self.logBuffer[1]) / (self.timeNow - self.logBuffer[0]) #výpočet rychlosti
                ySpeed = (self.yOrg - self.logBuffer[2]) / (self.timeNow - self.logBuffer[0])
                distance = math.sqrt(
                    math.pow((self.xOrg - self.logBuffer[1]), 2) + math.pow((self.yOrg - self.logBuffer[2]), 2))
                speed = distance / (self.timeNow - self.logBuffer[0]) #výpočet průměrné rychlosti
                '''
                Počítání vzdálenosti pomocí Pythagorovy věty. Bere se aktuální pozice robota (elf.xOrg,self.yOrg) 
                a předchozí pozicí hlavy robota (self.logBuffer[1], self.logBuffer[2]), pak je to klasicky, že
                vzdýlenost je odmocnina z aktuální pozice na druhou + předchozí pozice na druhou 
                '''
                acceleration = math.sqrt(
                    math.pow((xSpeed - self.logBuffer[3]), 2) + math.pow((ySpeed - self.logBuffer[4]), 2)) / (
                               self.timeNow - self.logBuffer[0])
                try:
                    if self.dataLogger.kind == 'dat': #zápis hodnot do dataloggeru
                        self.dataLogger(str(self.timeNow) + ' ' + str(self.xOrg) + ' ' + str(self.yOrg) + "\n")
                    elif self.dataLogger.kind == 'csv':
                        if self.logTitlesNeeded:
                            self.dataLogger(('time', 'x', 'y', 'xSpeed', 'ySpeed', 'distance', 'speed', 'acceleration'))
                            self.logTitlesNeeded = False

                        self.dataLogger((str(self.timeNow), str(self.xOrg), str(self.yOrg), str(xSpeed), str(ySpeed),
                                         str(distance), str(speed), str(acceleration))) 
                except:
                    pass

                self.logBuffer = [self.timeNow, self.xOrg, self.yOrg, xSpeed, ySpeed] #aktualizace proměnné, do které se ukládají hodnoty

            self.event.set()

    def _updatePositionFromRobot(self):
        self.evobot.send('M114')
        if not self.event.wait(1.0):
            print ("No message received before timeout when requesting head position")
        self.event.clear()

    def setDataLogger(self, logger):
        """
        This sets the data logger for the head. The data consist
        of the time, x, and y postions of the robot. The argument
        is a function that takes a string as input.
        """
        self.dataLogger = logger

    def park(self):
        """
        This method parks the head safely in preparation for shutdown
        of the robot. This is currently done by executing the home command.
        """
        self.home()

    def home(self):
        """
        This method homes the head by moving it to towards the switches.
        Once, the switches are engaged that position is defined to be (0,0).
        The method blocks the caller until the robot has completed
        the movement.
        """
        self.evobot._logUsrMsg('homing head...')
        self.evobot.send('G28')
        self._updatePositionFromRobot()
        while not (0.00 == self.x and 0.00 == self.y):
            self._updatePositionFromRobot()
        self.evobot._logUsrMsg('homed head')

    def move(self, x, y):
        """
        This method moves the head to the position (x,y) specified in mm.
        The method blocks the caller until the robot has completed
        the movement.
        """
        
        
        if x < 0 or x > self.xLimit or y < 0 or y > self.yLimit:
            self.evobot._logUsrMsg('head movements out of limits ' + str(x) + ", " + str(y))
            self.evobot.quit()

        x = round(x, 1)
        y = round(y, 1)
        self.evobot._logUsrMsg('head moving to: ' + str(x) + ' ' + str(y) + '...')

        moveToMsg = 'G1 X%f Z%f F%f' % (x, y, self.headSpeed)
        self.evobot.send(moveToMsg)
        self._updatePositionFromRobot()
        while not (x == self.x and y == self.y):
            self._updatePositionFromRobot()
        self.evobot._logUsrMsg('head moved')
    
    def moveXZ(self, x, y):
        self.move(x, y)
        
    def moveXY(self, x, z):
        """
        This method moves the head to the position (x,y) specified in mm.
        The method blocks the caller until the robot has completed
        the movement.
        """

        if x < 0 or x > self.xLimit or z < 0 or z > self.zLimit:
            self.evobot._logUsrMsg('head movements out of limits (XY)' + str(x) + ", " + str(z))
            self.evobot.quit()

        x = round(x, 1)
        z = round(z, 1)
        self.evobot._logUsrMsg('head moving to (XY): ' + str(x) + ' ' + str(z) + '...')

        moveToMsg = 'G1 X%f Y%f F%f' % (x, z, self.headSpeed)
        self.evobot.send(moveToMsg)
        self._updatePositionFromRobot()
        while not (x == self.x and z == self.z):
            self._updatePositionFromRobot()
        self.evobot._logUsrMsg('head moved')
        
    def moveYZ(self, z, y):
        """
        This method moves the head to the position (x,y) specified in mm.
        The method blocks the caller until the robot has completed
        the movement.
        """

        if y < 0 or y > self.yLimit or z < 0 or z > self.zLimit:
            self.evobot._logUsrMsg('head movements out of limits (moveYZ)' + str(z) + ", " + str(y))
            self.evobot.quit()

        y = round(y, 1)
        z = round(z, 1)
        self.evobot._logUsrMsg('head moving to (YZ): ' + str(z) + ' ' + str(y) + '...')

        moveToMsg = 'G1 Y%f Z%f F%f' % (z, y, self.headSpeed)
        self.evobot.send(moveToMsg)
        self._updatePositionFromRobot()
        while not (y == self.y and z == self.z):
            self._updatePositionFromRobot()
        self.evobot._logUsrMsg('head moved')
        
    def moveXYZ(self, x, z, y):
        """
        This method moves the head to the position (x, y, z) specified in mm.
        The method blocks the caller until the robot has completed
        the movement.
        """

        if x < 0 or x > self.xLimit or y < 0 or y > self.yLimit or z < 0 or z > self.zLimit:
            self.evobot._logUsrMsg('head movements out of limits (XYZ)' + str(x) + ", " + str(z) + ", " + str(y))
            self.evobot.quit()

        x = round(x, 1)
        y = round(y, 1)
        z = round(z, 1)
        self.evobot._logUsrMsg('head moving to (XYZ): ' + str(x) + ' ' + str(y) + ' ' + str(z) + '...')

        moveToMsg = 'G1 X%.1f Y%.1f Z%.1f F%.1f' % (x, z, y, self.headSpeed)
        print (moveToMsg)
        self.evobot.send(moveToMsg)
        self._updatePositionFromRobot()
        while not (x == self.x and y == self.y and z == self.z):
            self._updatePositionFromRobot()
        self.evobot._logUsrMsg('head moved')
    
    def moveXYZE(self, x, z, y, e0):
        """
        This method moves the head to the position (x, y, z, e0) specified in mm.
        The method blocks the caller until the robot has completed
        the movement.
        """

        if ( x < 0 or x > self.xLimit or y < 0 or y > self.yLimit or
            z < 0 or z > self.zLimit or e0 < 0 or e0 > self.e0Limit ):
            self.evobot._logUsrMsg('head movements out of limits (XYZE)' + str(x) + ", " + str(z) + ", " + str(y) + ", " + str(e0))
            self.evobot.quit()

        x = round(x, 1)
        y = round(y, 1)
        z = round(z, 1)
        e0 = round(e0, 1)
        self.evobot._logUsrMsg('head moving to (XYZE): ' + str(x) + ' ' + str(y) + ' ' + str(z) + ' ' + str(e0) + '...')

        moveToMsg = 'G1 X%f Y%f Z%f E%f F%f' % (x, z, y, e0, self.headSpeed)
        self.evobot.send(moveToMsg)
        self._updatePositionFromRobot()
        while not (x == self.x and y == self.y and z == self.z and e0 == self.e0):
            self._updatePositionFromRobot()
        self.evobot._logUsrMsg('head moved')
        

    def moveToCoord(self, coord):
        if len(coord) == 2:
            print ("coord0: ", coord[0], "coord1:", coord[1])
            self.move(coord[0], coord[1])
        else:
            self.evobot._logUsrMsg('coordinates does not have two parameters')
            self.evobot.quit()

    def moveContinously(self, x, y):
        """
        The method does not block the caller hence the robot may not have
        completed the movement before it returns.
        """

        if x <= 0 or x > self.xLimit or y < 0 or y > self.yLimit:
            self.evobot._logUsrMsg('head movements out of limits')
            self.evobot.quit()

        x = round(x, 1)
        y = round(y, 1)

        self.evobot._logUsrMsg('head moving to: ' + str(x) + ' ' + str(y) + '...')

        moveToMsg = 'G1 X%f Z%f' % (x, y)
        self.evobot.send(moveToMsg)
        if self.dataLogger is not None:
            try:
                if self.dataLogger.kind == 'dat':
                    self.dataLogger(
                        str(time.time() - self.evobot.iniTime) + ' ' + str(self.x) + ' ' + str(self.y) + "\n")
                elif self.dataLogger.kind == 'csv':
                    self.dataLogger((str(time.time() - self.evobot.iniTime), str(self.x), str(self.y)))
            except:
                pass

    def moveDiscrete(self, x, y, stepLength):

        """
        This method moves the head a stepLength towards position (x,y) unless the distance
        is short in which case it moves directly to (x,y). This is a none blocking call.
        """

        self.evobot._logUsrMsg('head moving discretely towards: ' + str(round(x, 1)) + ' ' + str(round(y, 1)) + '...')
        distance = math.pow(math.pow((x - self.x), 2) + math.pow((y - self.y), 2), .5)

        if stepLength > distance:  # we are close
            self.moveContinously(x, y)
        else:  # we are further away
            self.moveContinously(self.x + stepLength * (x - self.x) / distance,
                                 self.y + stepLength * (y - self.y) / distance)

        self.evobot._logUsrMsg('head moved discretely')

    def getX(self):
        """
        This returns the current x position of the robot
        """
        return self.x

    def getY(self):
        """
        This returns the current y position of the robot
        """
        return self.y
    
    def getZ(self):
        """
        This returns the current y position of the robot
        """
        return self.z

    def getE0(self):
        """
        This returns the current y position of the robot
        """
        return self.e0

    def getE1(self):
        """
        This returns the current y position of the robot
        """
        return self.e1
    
    def setSpeed(self, goalSpeed):
        """
        This method sets the speed of the head of the robot
        """
        if goalSpeed < 100 or goalSpeed > 9000:
            self.evobot._logUsrMsg('Head attempted to set its maximum speed to ' + str(
                goalSpeed) + 'mm/min, but exceed head speed\'s limits of [100:9000]')
            self.evobot.quit()

        goalSpeed = round(goalSpeed, 0)

        self.evobot._logUsrMsg('Setting head maximum speed to ' + str(goalSpeed) + 'mm/min')
        # moveToMsg = 'G1 F%f' % (goalSpeed)
        # self.evobot.send( moveToMsg )
        self.headSpeed = goalSpeed

        self.evobot._logUsrMsg('Plunger speed set')

    def getSpeed(self):
        """
        Returns the speed
        """
        return self.headSpeed
