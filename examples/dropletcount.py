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

startTime=time.time()

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
syringe1 =  Syringe( evobot, SYRINGES['SYRINGE1'])

#evobot.home()
evocam=EvoCam(evobot)
redDroplet=Droplet(color='default red', lowerhsv=None,upperhsv=None,minSizemm=None,maxSizemm=None,
                   minSizePix=5000,maxSizePix=6000,dataLoggerName='multitrackingred',contourColor='red')


blobs=Droplet(color='default red', lowerhsv=None,upperhsv=None,minSizemm=None,maxSizemm=None,
                    minSizePix=500,maxSizePix=20000,dataLoggerName='multitrackingblue',contourColor='blue')



evocam.trackDroplet(redDroplet,syringe1)
evocam.countBlobs(blobs,syringe1)
#evocam.record( 'dropletcount' , extension='.mkv')
evocam.openWindow()
while time.time() - startTime < 60 :
    evocam.updateWindow()
    print blobs.countBlobs()
    #if blobs.countBlobs()<3:
        #head.move(2,2)


evobot.disconnect()
#time.sleep(2)
evocam.disconnect()
