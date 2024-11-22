import time
import sys
sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from datalogger import DataLogger
from evobot import EvoBot
from head import Head

usrMsgLogger = DataLogger()
evobot = EvoBot("COM5", usrMsgLogger)
head = Head( evobot )

if not evobot.hasHomed():
    evobot.home()

while True:
    try:
        head.move( 10, 10) #na y byla 100
        head.move( 40,40 ) #90,100
    except KeyboardInterrupt:
        break

evobot.disconnect()
