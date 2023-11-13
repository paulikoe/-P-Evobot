import sys
import time
import datetime
import random
import Queue
from threading import Thread

sys.path.append('../settings')
from configuration import *


maxSyringes = 32


class robot:
    isOpen = False

    def __init__(self):
        self.headXcurrent = random.randint(0, 100)
        self.headYcurrent = random.randint(0, 100)
        self.pump1current = random.randint(0, 100)
        self.headXtarget = self.headXcurrent
        self.headYtarget = self.headYcurrent
        self.pump1target = self.pump1current

        self.syringeTargets = []
        self.syringeCurrents = []
        self.plungerTargets = []
        self.plungerCurrents = []

        i = 0
        while i < maxSyringes:
            self.syringeCurrents.append(-random.randint(0, 30))
            self.syringeTargets.append(self.syringeCurrents[i])
            self.plungerCurrents.append(-random.randint(0, 40))
            self.plungerTargets.append(self.plungerCurrents[i])
            i = i + 1

        self.motionControlRun = True
        self.motionControlThread = None
        self.messageBuffer = Queue.Queue()
        self.hasHomed = False

    def step(self, current, target):
        if abs(current - target) < 1:
            current = target
        if current > target:
            current -= 1
        elif current < target:
            current += 1
        return current

    def motionControl(self):

        previous = datetime.datetime.now()
        while( self.motionControlRun ):
            self.headXcurrent = self.step( self.headXcurrent, self.headXtarget )
            self.headYcurrent = self.step( self.headYcurrent, self.headYtarget )
            self.pump1current = self.step( self.pump1current, self.pump1target )
            i = 0
            while i<maxSyringes:
                self.syringeCurrents[i] = self.step( self.syringeCurrents[i], self.syringeTargets[i] )
                self.plungerCurrents[i] = self.step( self.plungerCurrents[i], self.plungerTargets[i] )
                i=i+1
            time.sleep(0) #0.05
#            now = datetime.datetime.now()
#            if ((now - previous).total_seconds()>3):
#                self.messageBuffer.put('STATUS I 0 S 32259 P 32262')
#                previous = datetime.datetime.now()
                
    def close(self):
        self.isOpen = False
        self.motionControlRun = False
        if self.motionControlThread is not None:
            self.motionControlThread.join()

    def connect(self, port, baud):
        self.motionControlThread = Thread(target=self.motionControl).start()
        self.isOpen = True

    def reset(self):
        print "RESET"

    def readline(self):
        for i in range(0, 10):
            if not self.messageBuffer.empty() and self.motionControlRun:
                break
            time.sleep(0.05)

        if not self.motionControlRun:
            self.messageBuffer.put("EOF")

        if self.messageBuffer.empty():
            self.messageBuffer.put("")

        return self.messageBuffer.get()

    def setTarget(self, var):
        if(var[0] == "X"):
            self.headXtarget = float(var.split('*')[0][1:])
            #print "new target (X): " + str(self.headXtarget)
        if(var[0] == "Z"):
            self.headYtarget = float(var.split('*')[0][1:])
            #print "new target (Z): " + str(self.headYtarget)
        if(var[0] == "E"):
            self.pump1target = float(var.split('*')[0][1:])
            #print "new target (E): " + str(self.pump1target)
        
        
    def write(self, string):
        # handles
        # N0 M291*41 - home syringe and plunger
        # N1 G28*18 - home head
        # N2 M114*37 - get current head position
        # TODO Add the other handles: setAcc, setSpeed, getVoltage, 
        
        terms = string.split()

        if terms[1].startswith('M292'):
            self.messageBuffer.put('ok')
            mesg = "PS"
            for j in SYRINGES:
                mesg += " " + str(SYRINGES[j]['ID'])
            self.messageBuffer.put(mesg)
        if terms[1].startswith('M291'):
            self.messageBuffer.put('ok')
            syringeID = int(terms[2].split('*')[0][1:])

            if len(terms) < 4:
                self.syringeTargets[syringeID] = 0
                self.plungerTargets[syringeID] = 0
            else:
                if terms[3].startswith('S'):
                    self.syringeTargets[syringeID] = 0
                if terms[3].startswith('P'):
                    self.plungerTargets[syringeID] = 0
        if terms[1].startswith('G28'):
            self.messageBuffer.put('ok')
            self.headXtarget = 0
            self.headYtarget = 0
            self.hasHomed = True
        if terms[1].startswith('M114'):
            self.messageBuffer.put('ok')
            self.messageBuffer.put("X:%f Y:0.0 Z:%f E:%f Count X: %f Y:0.0 Z:%f E:%f" % (
            self.headXtarget, self.headYtarget, self.pump1target, self.headXcurrent, self.headYcurrent, self.pump1current))
        if terms[1].startswith('G1'):
            self.messageBuffer.put('ok')
            for t in terms:
                self.setTarget(t) 
        if terms[1].startswith('M290'):
            self.messageBuffer.put('ok')
            if terms[2].startswith('I'):
                self.syringeID = int(terms[2].split('*')[0][1:])
            if len(terms) < 4:
                self.messageBuffer.put(
                    "I " + str(self.syringeID) + " S " + str(self.syringeCurrents[self.syringeID]) + " P " + str(
                        self.plungerCurrents[self.syringeID]))
            else:
                if terms[3].startswith('S'):
                    self.syringeTargets[self.syringeID] = float(terms[3].split('*')[0][1:])
                if terms[3].startswith('P'):
                    self.plungerTargets[self.syringeID] = float(terms[3].split('*')[0][1:])

        if terms[1].startswith('M298'):
            self.messageBuffer.put('ok')
            self.messageBuffer.put('HOMED FALSE')
        if terms[1].startswith('M112'):
            self.motionControlRun = False
        if terms[1].startswith('M285'):
            self.messageBuffer.put('ok')
            self.messageBuffer.put("V 0 M " + str(random.random() * 5))
        if terms[1].startswith('M295'):
            self.messageBuffer.put('ok')
        if terms[1].startswith('M296'):
            self.messageBuffer.put('ok')
        if terms[1].startswith('M286'):
            self.messageBuffer.put('ok')
            # TODO: Fix this. This only works if the output is switched on for some time.
            # TODO: It does not work when it is switched on indefinitely
            self.messageBuffer.put("M286 OFF OFF OFF ")
        time.sleep(0)
