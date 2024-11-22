import sys

sys.path.append('../api')
sys.path.append('../settings')
from local import *
from syringe import Syringe
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
import os
from servo import Servo
from dispenser import Dispenser

# This program homes the syringes, homes the head of the robot and moves the syringes up until the experimental layer.
# The robot is now ready to be turned off

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)

os.system("say 'Good evening Carlotta, thanks for another day in your presence! I am going to park all the syringes now' ")


syr1 = Syringe(evobot, SYRINGES['SYRINGE1'])
syr4 = Syringe(evobot, SYRINGES['SYRINGE4'])
syr11 = Syringe(evobot, SYRINGES['SYRINGE11'])
syr13 = Dispenser(evobot, SYRINGES['SYRINGE15'])
# servo2 = Servo(evobot, SERVOS['SERVO2'])
syr0 = Dispenser(evobot, SYRINGES['SYRINGE0'])

syr1.syringeSetSpeed(140)
syr4.syringeSetSpeed(140)
syr11.syringeSetSpeed(140)


syr13.home_dispenser()
syr0.home_dispenser()
syr1.homeSyringe()
syr4.homeSyringe()
syr11.homeSyringe()
# servo2.servoMove(0)


head.home()

syr1.syringeMove(-43)
syr4.syringeMove(-74)
syr11.syringeMove(-73)
syr13.dispenser_move(-60)
syr0.dispenser_move(-27)


evobot.disconnect()

