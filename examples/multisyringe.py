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
headLogger = DataLogger('experiments/headcomplex' + fileName, kind='csv')
syringe1 = Syringe(evobot, SYRINGES['SYRINGE1'])
syringe1Logger = DataLogger('experiments/syringe1complex' + fileName)
# this is to identify the world coordinate system. This is one of the syringes, we define the coordinates according to.
# 'mode' can be default or camera
worldcor = WorldCor(syringe1, mode='default')
wellplate = WellPlate(evobot, head, plateRows=8, plateCols=12, wellDiameter=9, tLeftCorner=(80, 5), dRightCorner=None,
                      worldCor=worldcor)
petridish1 = PetriDish(evobot, center=(0, 220), goalPos=-50, liquidType='water', worldCor=worldcor)
petridish2 = PetriDish(evobot, center=(140, 70), goalPos=-40, liquidType='water', worldCor=worldcor)

syringe2 = Syringe(evobot, SYRINGES['SYRINGE4'])
syringe2Logger = DataLogger('experiments/syringe2complex' + fileName)
syringeEventLogger = DataLogger('experiments/Eventcomplex' + fileName, kind='csv')

head.dataLogger = headLogger
syringe1.dataLogger = syringe1Logger
syringe2.dataLogger = syringe2Logger

evobot.home()
syringe1.plungerMoveToDefaultPos()
syringe2.plungerMoveToDefaultPos()

for row in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
    for column in xrange(1, 13):

        vol1 = 2
        if not syringe1.canDispenseVol(vol1):
            syringe1.fillVolFrom(head, ml='all', container=petridish1)
            syringeEventLogger(
                (str(syringe1.getXY(head, worldcor)[0]), str(syringe1.getXY(head, worldcor)[1]), 's1Fill'))

        wellplate.fillWell(syringe1, wellName=row + str(column), dispenseVol=vol1, dispensePos=-40, upPos=-38)
        syringeEventLogger((str(syringe1.getXY(head, worldcor)[0]), str(syringe1.getXY(head, worldcor)[1]), 's1well'))

        vol2 = 1
        if not syringe2.canDispenseVol(vol2):
            syringe2.fillVolFrom(head, ml='all', container=petridish2)
            syringeEventLogger(
                (str(syringe2.getXY(head, worldcor)[0]), str(syringe2.getXY(head, worldcor)[1]), 's2Fill'))
        wellplate.fillWell(syringe2, wellName=row + str(column), dispenseVol=vol2, dispensePos=-40, upPos=-38)
        syringeEventLogger((str(syringe2.getXY(head, worldcor)[0]), str(syringe2.getXY(head, worldcor)[1]), 's2well'))

# example for filling all wells
# wash syringe1 in the petridish
syringe1.syringe_wash(head, petridish1, petridish2, times=3, volume_clean_liquid=1)
# wash syringe2 in petridish
# syringe2.syringe_wash(head,times=3, offset=22, container=petridish)
# fill all wellplates with syringe2
# wellplate.fillAll(syringe2,petridish,dispenseVol=1,dispensePos=-30,upPos=-20)
# wellplate.emptyAll(syringe1,petridish,absorbVol=1,absorbPos=-30,upPos=-20)



"""
#uncomment for filling specific wells

#fill ml in syringe2, if ml='all', all the syringe will be filled from the container
syringe2.fillVolFrom( head, ml='all', container=petridish )

#fill specific well
wellplate.fillWell(syringe2,wellName='b3',dispenseVol=1,dispensePos=-35,upPos=-33)

#fill the 'E' row with syringe2
wellplate.fillWell(syringe2,wellName='E',dispenseVol=1,dispensePos=-35,upPos=-33)

#fill the '3' column with syringe1 
wellplate.fillWell(syringe1,wellName='3',dispenseVol=1,dispensePos=-35,upPos=-33)

#empty ml from syringe1, if ml='all', all the syringe will be emtied in the container
syringe1.emptyVolTo(head, ml='all', container=petridish)

"""

"""
# This is not needed except for some advanced applications!
#uncomment for finding the world coordiante equiavalent for a point 
#if a point is (100,100) in the world coordinate system (e.g. syringe1 in this example),
#to what position should we move the head so that syringe2 will be exactly at the same point in reality!
#to find the position of a point in world coordinate system (e.g. syringe1 in this example), try to move the head
#so syringe1 is going to that position(for example by pronterface) 

mm=worldcor.worldCorFor((100,100), syringe2)
head.move(int(mm[0]),int(mm[1]))
"""

# move syringe1 to the point (100,100) in the worldcoordinate system of syringe1
# syringe1.goToXY(head, (100,100), worldcor)
# move syringe2 to the point (100,100) in the worldcoordinate system of syringe1 (same point as above)
# syringe2.goToXY(head, (100,100), worldcor)




evobot.disconnect()
head.dataLogger.file.close()
syringe1.dataLogger.file.close()
syringeEventLogger.file.close()
