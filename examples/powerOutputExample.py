import time
import sys
sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from powerOutputs import PowerOutputs
from head import Head


usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
powerOutputs = PowerOutputs( evobot)

#Non-blocking method:
powerOutputs.turnOnD8()
powerOutputs.turnOnD9()
powerOutputs.turnOnD10()
time.sleep(3)
powerOutputs.turnOffD8()
powerOutputs.turnOffD9()
powerOutputs.turnOffD10()

#Blocking method, add time in milliseconds:
powerOutputs.turnOnD8(3000)
powerOutputs.turnOnD9(3000)
powerOutputs.turnOnD10(3000)

evobot.disconnect()