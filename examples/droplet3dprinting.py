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
from droplet3dprinter import Droplet3dPrinter

fileName=time.strftime("%Y-%m-%d %H%M%S")

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
headLogger = DataLogger( 'experiments/head3d' +fileName, kind='csv' )
syringe1 =  Syringe( evobot, SYRINGES['SYRINGE1'])
syringeLogger = DataLogger( 'experiments/syringe3d' + fileName )
#this is to identify the world coordinate system. This is one of the syringes, we define the coordinates according to.
#mode can be default or camera
worldcor=WorldCor(syringe1, mode='default')
wellplate=WellPlate(evobot,head, plateRows=8, plateCols = 12 , wellDiameter=9, tLeftCorner=(80,120), dRightCorner=None, worldCor=worldcor)
petridish=PetriDish(evobot, center=(70,10),goalPos=-30, liquidType='water' , worldCor=worldcor) 

droplet3dprinter=Droplet3dPrinter(evobot,head,syringe1, worldcor)
pushEventLogger = DataLogger( 'experiments/push3d' +fileName, kind='csv' )


head.dataLogger = headLogger
syringe1.dataLogger = syringeLogger
droplet3dprinter.dataLogger = pushEventLogger


evobot.home()
droplet3dprinter.startPrint(printString= 'R E A L ',printPoint=(130,0),dimensions=(80,320),dispenseVol=0.05 , minDistancemm=3, goalPos=-50, upPos=-48)

evobot.disconnect()
head.dataLogger.file.close()
syringe1.dataLogger.file.close()
droplet3dprinter.dataLogger.file.close()