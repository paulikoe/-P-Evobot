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
evobot = EvoBot("COM5", usrMsgLogger)
head = Head(evobot)
syringe = Syringe(evobot, SYRINGES['SYRINGE1'])
evobot.home()

syringe.plungerMoveToDefaultPos()
while True:
    try:

        # Setting the maximum speed
        # TODO: Set the maximum acc for the head
        head.setSpeed(9000)
        syringe.syringeSetSpeed(1500)
        syringe.syringeSetAcc(1500)
        syringe.plungerSetSpeed(288)
        syringe.plungerSetAcc(96)

        head.move(20, 100)
        syringe.syringeMove(-30)
        syringe.plungerPullVol(5)
        syringe.syringeMove(0)

        # Setting the minimum speed
        # TODO: Set the minimum speed acc for the head
        head.setSpeed(100)
        syringe.syringeSetSpeed(50)
        syringe.syringeSetAcc(50)
        syringe.plungerSetSpeed(12)
        syringe.plungerSetAcc(12)

        head.move(90, 100)
        syringe.syringeMove(-30)
        syringe.plungerPushVol(5)
        syringe.syringeMove(0)

    except KeyboardInterrupt:
        break

evobot.disconnect()
