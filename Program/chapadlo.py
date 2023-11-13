import sys
import time
sys.path.append('../api') #open the file api 
sys.path.append('../settings')

from configuration import *
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
from gripper import Gripper
from perpump import Perpump

data = DataLogger()
evobot = EvoBot("COM5", data)
head = Head(evobot)
gripper = Gripper(evobot,GRIPPERS["GRIPPER1"]) #viz settings - local
perpump = Perpump(evobot)

evobot.home()
if not evobot.hasHomed():
    evobot.home()

i = 0
while i<1:
    try:
        #head.move(0,200)
        gripper.gripperMove(-49.9940)
        time.sleep(2)
        perpump.start()
        time.sleep(2)
        #gripper.gripperMove(0)
        #head.move(200,200)
        #gripper.gripperMove(-60)
        perpump.stop()
        evobot.home()
        #gripper.gripperMove(-50)
    except KeyboardInterrupt:
        break

    i += 1




'''
Ultrazvukový senzor bude posílat data v nějaké formě - tyto data musím číst a zpracovat je. Udělat PID regulátor.
Žádaná hodnota - když
'''