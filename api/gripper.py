<<<<<<< HEAD
import time
import threading
import datetime
import sys
from head import Head
from petridish import PetriDish
from worldcor import WorldCor
import os
import numpy as np


class Gripper:
    def __init__(self, _evobot, gripperConfig):
        """
     
        """
        self.gripperID = gripperConfig['ID']
        self.evobot = _evobot

        if not str(self.gripperID) in self.evobot.populatedSockets:
            self.evobot._logUsrMsg('gripper initialization failed: no gripper on socket ' + str(self.gripperID))
            self.evobot._logUsrMsg('Available sockets: ' + str(self.evobot.populatedSockets))
            self.evobot.quit()
            return

        self.gripperPos = -1  # mm
        self.gripperLimit = gripperConfig['GRIPPER_LIMIT']  # this is when the gripper is completely push down
        
        self.dateLogger = None
        self.evobot.modules.append(self)
        self.event = threading.Event()
        self.logBuffer = [0, 0, 0, 0, 0]
        self.logTitlesNeeded = True
        fname = '../calibration/affinemat/' + str(self.gripperID) + '.npy'
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
            if (self.gripperID == int(terms[1])):
                self.gripperPos = round(float(terms[3]), 2)
                self.event.set()
                if self.dataLogger is not None:
                    timeNow = time.time() - self.evobot.iniTime
                    sSpeed = (self.gripperPos - self.logBuffer[1]) / (timeNow - self.logBuffer[0])
                    sAcceleration = (sSpeed - self.logBuffer[2]) / (timeNow - self.logBuffer[0])
                    try:
                        if self.dataLogger.kind == 'dat':
                            self.dataLogger(str(time.time() - self.evobot.iniTime) + ' ' + str(self.gripperPos) + "\n")
                        elif self.dataLogger.kind == 'csv':
                            if self.logTitlesNeeded:
                                self.dataLogger(('time', 'gripperPos', 'sSpeed', 'sAcceleration'))
                                self.logTitlesNeeded = False

                            self.dataLogger((str(timeNow), str(self.gripperPos), str(sSpeed), str(sAcceleration)))
                    except:
                        pass
                    self.logBuffer = [timeNow, self.gripperPos, sSpeed]

    def _getPos(self):
        """
        Private method that is internally used in the class to obtain
        the positions of the gripper.
        """

        gripperGetPosMsg = 'M290 I' + str(self.gripperID)
        self.evobot.send(gripperGetPosMsg)
        if not self.event.wait(1.0):
            print ("No message received before timeout when requesting gripper position")
        self.event.clear()

    def gripperGetPos(self):
        """
        This method returns the position of the gripper in mm.
        """

        self._getPos()
        return self.gripperPos
    
    def setDataLogger(self, logger):
        """
        This sets the data logger for the head. The data logged consist
        of the time and scanner position. The argument
        is a function that takes a string as input.
        """

        self.dataLogger = logger

    def gripperMove(self, goalPos):  # mm
        """
        This move the gripper mm. This is a blocking call, hence, control
        is not returned to the caller until the gripper has finished moving.
        """

        if goalPos > 0 or goalPos < self.gripperLimit:
            self.evobot._logUsrMsg('gripper attempt to move past limits of [0:' + str(self.gripperLimit) + ']')
            return
            # self.evobot.quit()

        goalPos = round(goalPos, 1)

        self.evobot._logUsrMsg('Gripper moving to ' + str(goalPos) + 'mm (absolute)')

        gripperMoveMsg = 'M290 I' + str(self.gripperID) + ' S' + str(goalPos)
        self.evobot.send(gripperMoveMsg)
        now = datetime.datetime.now()
        '''
        while not self.gripperGetPos() == goalPos:
            self._getPos()
            time_delta = (datetime.datetime.now() - now)

            if time_delta > datetime.timedelta(seconds=5):
                self.evobot._logUsrMsg("Timeout when moving the gripper.")
                self.evobot._logUsrMsg("Goal pos: " + str(goalPos) + " Gripper pos: " + str(self.gripperGetPos()))
                gripperStatusMsg = 'M289 I' + str(self.gripperID)
                self.evobot.send(gripperStatusMsg)
                time.sleep(2)
                self.evobot._logUsrMsg("Trying to move the gripper again...")
                self.evobot.send(gripperMoveMsg)
                now = datetime.datetime.now()
        '''
        self.evobot._logUsrMsg('Gripper moved')
    
    def gripperRise(self, mm):
        """
        This method rises mm millimeters the gripper .
        """

        self.evobot._logUsrMsg('Gripper rising ' + str(mm) + 'mm')
        self.gripperMovePos(self.gripperPos - mm)
        self.evobot._logUsrMsg('Gripper rised')

    def gripperDescend(self, mm):
        """
        This method descends mm millimeters the gripper .
        """

        self.evobot._logUsrMsg('Gripper descending ' + str(mm) + 'mm')
        self.gripperMovePos(self.gripperPos + mm)
        self.evobot._logUsrMsg('Gripper descended')

    def gripperMoveRel(self, mm):
        """
        This method is convenience function that descends mm millimiters 
        if mm is negative and rises mm millimeters if mm is positive.
        """
        if mm < 0:
            self.gripperDescend(-mm)
        else:
            self.gripperRise(mm)

    def homeGripper(self):
        """
        This homes the gripper by moving it to its
        upper most position where the homing switch is activated.
        """

        self.evobot._logUsrMsg('homing gripper (gripper only, not plunger)' + str(self.gripperID))
        homeGripperMsg = 'M291 I' + str(self.gripperID) + " S"
        self.evobot.send(homeGripperMsg)
        now = datetime.datetime.now()
        while not self.gripperGetPos() == 0:
            self._getPos()
            

        self.evobot._logUsrMsg('homed gripper')
    def home(self):
        """
        This homes the scaner by moving it to its
        upper most position where the homing switch is activated.
        """
        self.homeGripper()
        #self.evobot._logUsrMsg('homing gripper ' + str(self.gripperID))
        #self.evobot.send('M291 I' + str(self.gripperID))
        #while not self.gripperGetPos() == 0:
        #    pass

        #self.evobot._logUsrMsg('homed gripper')

    def park(self):
        self.gripperMovePos(0)
    
    def goToXY(self, head, point, worldcor):
        # TODO: This is not working well (the gripper module is different from
        # a syringe in the same socket), we must fix it 

        mm = worldcor.worldCorFor((point[0], point[1]), self.gripperID)
        head.move(round(float(mm[0]), 2), round(float(mm[1]), 2))

    def getXY(self, head, worldcor):
        # TODO: This is not working well (the gripper module is different from
        # a syringe in the same socket), we must fix it 

        mm = worldcor.inverseWorldCorFor((head.getX(), head.getY()), self.gripperID)
        return round(float(mm[0]), 2), round(float(mm[1]), 2)

=======
import time
import threading
import datetime
import sys
from head import Head
from petridish import PetriDish
from worldcor import WorldCor
import os
import numpy as np


class Gripper:
    def __init__(self, _evobot, gripperConfig):
        """
     
        """
        self.gripperID = gripperConfig['ID']
        self.evobot = _evobot

        if not str(self.gripperID) in self.evobot.populatedSockets:
            self.evobot._logUsrMsg('gripper initialization failed: no gripper on socket ' + str(self.gripperID))
            self.evobot._logUsrMsg('Available sockets: ' + str(self.evobot.populatedSockets))
            self.evobot.quit()
            return

        self.gripperPos = -1  # mm
        self.gripperLimit = gripperConfig['GRIPPER_LIMIT']  # this is when the gripper is completely push down
        
        self.dateLogger = None
        self.evobot.modules.append(self)
        self.event = threading.Event()
        self.logBuffer = [0, 0, 0, 0, 0]
        self.logTitlesNeeded = True
        fname = '../calibration/affinemat/' + str(self.gripperID) + '.npy'
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
            if (self.gripperID == int(terms[1])):
                self.gripperPos = round(float(terms[3]), 2)
                self.event.set()
                if self.dataLogger is not None:
                    timeNow = time.time() - self.evobot.iniTime
                    sSpeed = (self.gripperPos - self.logBuffer[1]) / (timeNow - self.logBuffer[0])
                    sAcceleration = (sSpeed - self.logBuffer[2]) / (timeNow - self.logBuffer[0])
                    try:
                        if self.dataLogger.kind == 'dat':
                            self.dataLogger(str(time.time() - self.evobot.iniTime) + ' ' + str(self.gripperPos) + "\n")
                        elif self.dataLogger.kind == 'csv':
                            if self.logTitlesNeeded:
                                self.dataLogger(('time', 'gripperPos', 'sSpeed', 'sAcceleration'))
                                self.logTitlesNeeded = False

                            self.dataLogger((str(timeNow), str(self.gripperPos), str(sSpeed), str(sAcceleration)))
                    except:
                        pass
                    self.logBuffer = [timeNow, self.gripperPos, sSpeed]

    def _getPos(self):
        """
        Private method that is internally used in the class to obtain
        the positions of the gripper.
        """

        gripperGetPosMsg = 'M290 I' + str(self.gripperID)
        self.evobot.send(gripperGetPosMsg)
        if not self.event.wait(1.0):
            print ("No message received before timeout when requesting gripper position")
        self.event.clear()

    def gripperGetPos(self):
        """
        This method returns the position of the gripper in mm.
        """

        self._getPos()
        return self.gripperPos
    
    def setDataLogger(self, logger):
        """
        This sets the data logger for the head. The data logged consist
        of the time and gripper position. The argument
        is a function that takes a string as input.
        """

        self.dataLogger = logger

    def gripperMove(self, goalPos):  # mm
        """
        This move the gripper mm. This is a blocking call, hence, control
        is not returned to the caller until the gripper has finished moving.
        """

        if goalPos > 0 or goalPos < self.gripperLimit:
            self.evobot._logUsrMsg('gripper attempt to move past limits of [0:' + str(self.gripperLimit) + ']')
            return
            # self.evobot.quit()

        goalPos = round(goalPos, 1)

        self.evobot._logUsrMsg('Gripper moving to ' + str(goalPos) + 'mm (absolute)')

        gripperMoveMsg = 'M290 I' + str(self.gripperID) + ' S' + str(goalPos)
        self.evobot.send(gripperMoveMsg)
        now = datetime.datetime.now()

        #aby to nekontrolovalo na jaké pozici se nachází, chceme tu, kterou zadáme
        '''
        while not self.gripperGetPos() == goalPos:
            self._getPos()
            time_delta = (datetime.datetime.now() - now)

            if time_delta > datetime.timedelta(seconds=5):
                self.evobot._logUsrMsg("Timeout when moving the gripper.")
                self.evobot._logUsrMsg("Goal pos: " + str(goalPos) + " Gripper pos: " + str(self.gripperGetPos()))
                gripperStatusMsg = 'M289 I' + str(self.gripperID)
                self.evobot.send(gripperStatusMsg)
                time.sleep(2)
                self.evobot._logUsrMsg("Trying to move the gripper again...")
                self.evobot.send(gripperMoveMsg)
                now = datetime.datetime.now()
        '''
        self.evobot._logUsrMsg('Gripper moved')
    
    def gripperRise(self, mm):
        """
        This method rises mm millimeters the gripper .
        """

        self.evobot._logUsrMsg('Gripper rising ' + str(mm) + 'mm')
        self.gripperMovePos(self.gripperPos - mm)
        self.evobot._logUsrMsg('Gripper rised')

    def gripperDescend(self, mm):
        """
        This method descends mm millimeters the gripper .
        """

        self.evobot._logUsrMsg('Gripper descending ' + str(mm) + 'mm')
        self.gripperMovePos(self.gripperPos + mm)
        self.evobot._logUsrMsg('Gripper descended')

    def gripperMoveRel(self, mm):
        """
        This method is convenience function that descends mm millimiters 
        if mm is negative and rises mm millimeters if mm is positive.
        """
        if mm < 0:
            self.gripperDescend(-mm)
        else:
            self.gripperRise(mm)

    def homeGripper(self):
        """
        This homes the gripper by moving it to its
        upper most position where the homing switch is activated.
        """

        self.evobot._logUsrMsg('homing gripper (gripper only, not plunger)' + str(self.gripperID))
        homeGripperMsg = 'M291 I' + str(self.gripperID) + " S"
        self.evobot.send(homeGripperMsg)
        now = datetime.datetime.now()
        while not self.gripperGetPos() == 0:
            self._getPos()
            

        self.evobot._logUsrMsg('homed gripper')
    def home(self):
        """
        This homes the gripper by moving it to its
        upper most position where the homing switch is activated.
        """
        self.homeGripper()
        #Nutné zakomentovat, aby se to nesnazilo najit i druhý krokový motor
        #self.evobot._logUsrMsg('homing gripper ' + str(self.gripperID))
        #self.evobot.send('M291 I' + str(self.gripperID))
        #while not self.gripperGetPos() == 0:
        #    pass

        #self.evobot._logUsrMsg('homed gripper')

    def park(self):
        self.gripperMovePos(0)
    
    def goToXY(self, head, point, worldcor):
        # TODO: This is not working well (the gripper module is different from
        # a syringe in the same socket), we must fix it 

        mm = worldcor.worldCorFor((point[0], point[1]), self.gripperID)
        head.move(round(float(mm[0]), 2), round(float(mm[1]), 2))

    def getXY(self, head, worldcor):
        # TODO: This is not working well (the gripper module is different from
        # a syringe in the same socket), we must fix it 

        mm = worldcor.inverseWorldCorFor((head.getX(), head.getY()), self.gripperID)
        return round(float(mm[0]), 2), round(float(mm[1]), 2)

>>>>>>> 344c0c8 (large file to github)
