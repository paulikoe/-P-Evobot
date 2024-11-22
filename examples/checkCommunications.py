import time
import sys

sys.path.append('../api')
sys.path.append('../settings')
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from configuration import *

pos1x,pos1y = 50, 100
pos2x,pos2y = 60, 90


usrMsgLogger = DataLogger()
evobot = EvoBot("COM5", usrMsgLogger)
head = Head( evobot )
#syringe = Syringe(evobot, SYRINGE0)
evobot.home()
head.setSpeed(9000)


for iter in range(0,20000):
    head.move( pos1x, pos1y )
    head.move( pos2x, pos2y )
    print ("Finished iter " + str(iter))

