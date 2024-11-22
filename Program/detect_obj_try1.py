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
evobot = EvoBot("COM6", data)
head = Head(evobot)
gripper = Gripper(evobot,GRIPPERS["GRIPPER1"]) #viz settings - local
perpump = Perpump(evobot)

evobot.home()
if not evobot.hasHomed():
    evobot.home()

i = 0
while i<1:
    try:
        head.move(200,400)
    except KeyboardInterrupt:
        break

    i += 1

