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
headLogger = DataLogger('experiments/head' + fileName, kind='csv')
syringe1 = Syringe(evobot, SYRINGES['SYRINGE1'])
syringeLogger = DataLogger('experiments/syringe' + fileName)
# this is to identify the world coordinate system. This is one of the syringes, we define the coordinates according to.
# mode can be default or camera
worldcor = WorldCor(syringe1, mode='default')
wellplate = WellPlate(evobot, head, plateRows=8, plateCols=12, wellDiameter=9, tLeftCorner=(80, 120), dRightCorner=None,
                      worldCor=worldcor)
petridish = PetriDish(evobot, center=(70, 10), goalPos=-30, liquidType='water', worldCor=worldcor)
petridish1 = PetriDish(evobot, center=(20, 10), goalPos=-30, liquidType='water', worldCor=worldcor)
petridish2 = PetriDish(evobot, center=(30, 10), goalPos=-30, liquidType='water', worldCor=worldcor)

head.dataLogger = headLogger
syringe1.dataLogger = syringeLogger
# syringe2 =  Syringe( evobot, SYRINGE2)
# syringe2.plungerSetConversion( PLUNGER_CONVERSION_FACTOR )
evobot.home()

# example for filling all wells
# wash syringe1 in the petridish
syringe1.syringe_wash(head, petridish1, petridish2, times=3, volume_clean_liquid=1)
# wash syringe2 in petridish
# syringe2.syringe_wash(head,times=3, offset=22, container=petridish)
# fill all wellplates with syringe2
wellplate.fillAll(syringe1, petridish, dispenseVol=1, dispensePos=-35, upPos=-30)

evobot.disconnect()
head.dataLogger.file.close()
syringe1.dataLogger.file.close()
