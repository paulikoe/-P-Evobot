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
headLogger = DataLogger('experiments/headnton' + fileName, kind='csv')
syringe1 = Syringe(evobot, SYRINGES['SYRINGE1'])
syringeLogger = DataLogger('experiments/syringenton' + fileName)
# this is to identify the world coordinate system. This is one of the syringes, we define the coordinates according to.
# mode can be default or camera
worldcor = WorldCor(syringe1, mode='default')
wellplate = WellPlate(evobot, head, plateRows=8, plateCols=12, wellDiameter=9, tLeftCorner=(80, 0), dRightCorner=None,
                      worldCor=worldcor)
wellplate2 = WellPlate(evobot, head, plateRows=8, plateCols=12, wellDiameter=9, tLeftCorner=(185, 120),
                       dRightCorner=None, worldCor=worldcor)
petridish = PetriDish(evobot, center=(70, 10), goalPos=-50, liquidType='water', worldCor=worldcor)

head.dataLogger = headLogger
syringe1.dataLogger = syringeLogger

evobot.home()
syringe1.plungerMoveToDefaultPos()

# syringe1.syringe_wash(head,times=1, offset=22, container=petridish)
# fill all wellplates with syringe1
# wellplate.fillAll(syringe1,petridish,dispenseVol=1,dispensePos=-40,upPos=-38)
# transfer contents of one wellplate to another 
wellplate.transferToWellplate(syringe1, wellplate2, absorbVol=2, absorbPos=-40, upPos=-38)

evobot.disconnect()
head.dataLogger.file.close()
syringe1.dataLogger.file.close()
