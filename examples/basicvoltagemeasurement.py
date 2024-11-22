import time
import sys

sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from voltagesensor import VoltageSensor
from datalogger import DataLogger

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
voltagesensor = VoltageSensor( evobot, 0 )

while True:
    print voltagesensor.getMeasurement()
    time.sleep(1)
