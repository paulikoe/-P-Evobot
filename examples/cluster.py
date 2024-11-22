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
fileName = time.strftime("%Y-%m-%d %H%M%S")

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)
syringeDec = Syringe(evobot, SYRINGES['SYRINGE11'])
syringeAq = Syringe(evobot, SYRINGES['SYRINGE1'])
numberLogger = DataLogger('experiments/cluster' + fileName, kind='csv')
decanol = [49, 0]
deconate = [49, 92]
salt = [24, 118]
slideR = [105, 223]
slideDown = -38
slideL = [105, 195]

worldcor = WorldCor(syringeDec, mode='default')
# wellplate=WellPlate(evobot,head, plateRows=8, plateCols = 12 , wellDiameter=9, tLeftCorner=(80,5), dRightCorner=None, worldCor=worldcor)
petridish1 = PetriDish(evobot, center=(0, 100), goalPos=-30, liquidType='water', worldCor=worldcor)
petridish2 = PetriDish(evobot, center=(0, 100), goalPos=-35, liquidType='water', worldCor=worldcor)
# wellplate for decanol
petriDec = PetriDish(evobot, center=(49, 0), goalPos=-30, liquidType='water', worldCor=worldcor)
petriDeconate = PetriDish(evobot, center=(49, 92), goalPos=-34, liquidType='water', worldCor=worldcor)

evobot.home()
evocam = EvoCam(evobot)
evocam.record('cluster', extension='.mkv')
# empty syringes
syringeDec.emptyVolTo(head, ml='all', container=petridish1)
syringeAq.emptyVolTo(head, ml='all', container=petridish2)

# deconate
head.move(deconate[0], deconate[1])
syringeAq.syringeMove(-34)
syringeAq.plungerPullVol(15)
syringeAq.plungerPushVol(0.1)
syringeAq.syringeMove(0)

# slide left
head.move(slideL[0], slideL[1])
syringeAq.syringeMove(slideDown)
syringeAq.plungerPushVol(2.5)
syringeAq.syringeMove(0)

# slide right
head.move(slideR[0], slideR[1])
syringeAq.syringeMove(slideDown)
syringeAq.plungerPushVol(2.5)
syringeAq.syringeMove(0)

# empty syringe from decanoate and wash syringeAq
# syringeAq.emptyVolTo(head, ml='all', container=petriDeconate)
syringeAq.syringe_wash(head, petridish1, petridish2, times=3, volume_clean_liquid=1)

# decanol
head.move(decanol[0], decanol[1])
syringeDec.syringeMove(-40)
syringeDec.plungerPullVol(2)
syringeDec.plungerPushVol(.5)
syringeDec.syringeMove(0)


def addCluster():
    for x in [0, 10]:
        for y in [0, 10, 20, 30, 40]:
            head.move(101 + x, 75 + y)
            syringeDec.syringeMove(-47)
            syringeDec.plungerPushVol(.1)
            time.sleep(1)
            syringeDec.syringeMove(-40)
    syringeDec.syringeMove(0)
    head.move(35, 0)


def getSalt():
    syringeAq.syringeMove(0)
    head.move(salt[0], salt[1])
    syringeAq.syringeMove(-34)
    syringeAq.plungerPullVol(2)
    syringeAq.plungerPushVol(.5)
    syringeAq.syringeMove(0)

    # go to slide
    head.move(slideL[0], slideL[1] + 26)
    syringeAq.syringeMove(slideDown)
    syringeAq.plungerPushVol(.3)
    syringeAq.syringeMove(0)


# add decanol cluster to slide
addCluster()

blobs = Droplet(color='default red', lowerhsv=None, upperhsv=None, minSizemm=None, maxSizemm=None,
                minSizePix=50, maxSizePix=20000, dataLoggerName='multitrackingblue', contourColor='blue')

# evocam.trackDroplet(redDroplet,syringeDec)
evocam.countBlobs(blobs, syringeDec)
evocam.openWindow()
while time.time() - startTime < 600:
    evocam.updateWindow()
    timeNow = time.time() - startTime
    numberLogger((str(timeNow), str(blobs.countBlobs())))
    print blobs.countBlobs()
    if blobs.countBlobs() == 1:
        getSalt()
        break

time.sleep(60)
syringeDec.emptyVolTo(head, ml='all', container=petriDec)

evobot.disconnect()
numberLogger.file.close()
evocam.disconnect()
