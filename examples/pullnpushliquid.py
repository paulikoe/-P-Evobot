import time
import sys

sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)
syringe = Syringe(evobot, SYRINGES['SYRINGE1'])
evobot.home()

syringe.plungerMoveToDefaultPos()
while True:
    try:
        head.move(20, 100)
        syringe.syringeMove(-30)
        syringe.plungerPullVol(5)
        syringe.syringeMove(0)
        head.move(90, 100)
        syringe.plungerPushVol(5)
    except KeyboardInterrupt:
        break

evobot.disconnect()
