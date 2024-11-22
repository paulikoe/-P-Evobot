import sys
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from pump import Pump
from head import Head
sys.path.append('../api')
sys.path.append('../settings')

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)
pump = Pump(evobot, PUMPS['PUMP1'])

head.home()
pump.setSpeed(200)
pump.pumpPushVol(20)
pump.continuous_dispensation_of_liquid((50,50), 9 , 40)
#pump.pumpPullVol(12)
#pump.pumpPushVol(5)
evobot.disconnect()
