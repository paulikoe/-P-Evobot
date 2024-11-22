import time
import sys

sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from wellplate import WellPlate
from petridish import PetriDish
from worldcor import WorldCor
from droplet import Droplet
from evocam import EvoCam
import time

startTime = time.time()

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)
syringe1 = Syringe(evobot, SYRINGES['SYRINGE1'])
worldcor = WorldCor(syringe1, mode='default')

evobot.home()
evocam = EvoCam(evobot)
redDroplet = Droplet(color='default red', lowerhsv=None, upperhsv=None, minSizemm=None, maxSizemm=None,
                     minSizePix=100, maxSizePix=7000, dataLoggerName='multitrackingred', contourColor='red')

evocam.trackDroplet(redDroplet, syringe1)
evocam.record('multi', extension='.mkv')
evocam.openWindow()
while time.time() - startTime < 100:
    evocam.updateWindow(redDroplet)
    if redDroplet.isSpeedBelow(threshmmps=None, threshpixpfr=200, time=5):
        syringe1.goToXY(head, (redDroplet.getPosMM()[0] + 10, redDroplet.getPosMM()[1] + 10), worldcor)

evobot.disconnect()
evocam.disconnect()
