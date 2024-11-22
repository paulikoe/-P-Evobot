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
headLogger = DataLogger('experiments/head1ton' + fileName, kind='csv')
syringe1 = Syringe(evobot, SYRINGES['SYRINGE1'])
syringeLogger = DataLogger('experiments/syringe1ton' + fileName)
# this is to identify the world coordinate system. This is one of the syringes, we define the coordinates according to.
# mode can be default or camera
worldcor = WorldCor(syringe1, mode='default')
wellplate = WellPlate(evobot, head, plateRows=1, plateCols=2, wellDiameter=9, tLeftCorner=(80, 120), dRightCorner=None,
                      worldCor=worldcor)
petridish = PetriDish(evobot, center=(70, 10), goalPos=-50, liquidType='water', worldCor=worldcor)

head.dataLogger = headLogger
syringe1.dataLogger = syringeLogger

evobot.home()
print 'washing syringes'
# syringe1.syringe_wash(head, times=1, volume_clean_liquid = 1, container_waste=petridish1, container_clean=petridish2)
# fill all wellplates with syringe1
wellplate.fillAll(syringe1, petridish, dispenseVol=1, dispensePos=-40, upPos=-38)
evobot.disconnect()
head.dataLogger.file.close()
syringe1.dataLogger.file.close()
