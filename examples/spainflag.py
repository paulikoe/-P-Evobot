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
syringe2 =  Syringe( evobot, SYRINGES['SYRINGE2'])
#this is to identify the world coordinate system. This is one of the syringes, we define the coordinates according to.
#mode can be default or camera
worldcor=WorldCor(syringe1, mode='default')
wellplate=WellPlate(evobot,head, plateRows=8, plateCols = 12 , wellDiameter=3, tLeftCorner=(110,160), dRightCorner=None, worldCor=worldcor)
redPetridish=PetriDish(evobot, center=(184,80),goalPos=-22, liquidType='water' , worldCor=worldcor)
yellowPetridish=PetriDish(evobot, center=(200,150),goalPos=-22, liquidType='water' , worldCor=worldcor)  

droplet3dprinter=Droplet3dPrinter(evobot,head,syringe1, worldcor)



evobot.home()


syringe1.emptyVolTo( head, ml= 'all', container= redPetridish )
syringe1.fillVolFrom( head, ml= 'all', container= redPetridish )
syringe1.emptyVolTo( head, ml= 2, container= redPetridish )
droplet3dprinter.startPrint(printString= 'R E A L ',printPoint=(130,0),dimensions=(80,320),dispenseVol=0.05 , minDistancemm=3, goalPos=-25, upPos=-22)



for row in ['a','b']:
    for column in xrange(1,13):

        vol1=0.05
        if not syringe1.canDispenseVol(vol1):
            syringe1.fillVolFrom( head, ml='all', container= redPetridish)
        wellplate.fillWell(syringe1,wellName=row + str(column),dispenseVol=vol1,dispensePos=-25,upPos=-22)

syringe2.emptyVolTo( head, ml= 'all', container= yellowPetridish )
syringe2.fillVolFrom( head, ml= 'all', container= yellowPetridish )
syringe2.emptyVolTo( head, ml= 2, container= yellowPetridish )
for row in ['c','d','e','f']:
    for column in xrange(1,13):

        vol1=0.05 
        wellplate.fillWell(syringe2,wellName=row + str(column),dispenseVol=vol1,dispensePos=-24.5,upPos=-22)

for row in ['g','h']:
    for column in xrange(1,13):

        vol1=0.05
        if not syringe1.canDispenseVol(vol1):
            syringe1.fillVolFrom( head, ml='all', container= redPetridish)
        wellplate.fillWell(syringe1,wellName=row + str(column),dispenseVol=vol1,dispensePos=-25,upPos=-22)

        

syringe2.emptyVolTo( head, ml= 'all', container= yellowPetridish )
syringe1.emptyVolTo( head, ml= 'all', container= redPetridish )


evobot.disconnect()