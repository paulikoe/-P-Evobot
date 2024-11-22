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

fileName = time.strftime("%Y-%m-%d %H%M%S")

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)
headLogger = DataLogger('experiments/headnto1' + fileName, kind='csv')
syringe1 = Syringe(evobot, SYRINGES['SYRINGE1'])
syringeLogger = DataLogger('experiments/syringento1' + fileName)
# this is to identify the world coordinate system. This is one of the syringes, we define the coordinates according to.
# mode can be default or camera
worldcor = WorldCor(syringe1, mode='default')
wellplate = WellPlate(evobot, head, plateRows=8, plateCols=12, wellDiameter=9, tLeftCorner=(80, 5), dRightCorner=None,
                      worldCor=worldcor)
petridish = PetriDish(evobot, center=(185, 220), goalPos=-50, liquidType='water', worldCor=worldcor)

head.dataLogger = headLogger
syringe1.dataLogger = syringeLogger

evobot.home()
# empty all wellplates with syringe1
wellplate.emptyAll(syringe1, petridish, absorbVol=1, absorbPos=-40, upPos=-38)
evobot.disconnect()
head.dataLogger.file.close()
syringe1.dataLogger.file.close()
