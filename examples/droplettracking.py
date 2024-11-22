# This program moves the syringe to a specific position and makes a droplet, it then waits two seconds and then charges after
# the droplet and absorbs it and move it back to the starting point.

import sys
import signal
import time
import math
sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
#from wellplate import WellPlate
#from petridish import PetriDish
#from worldcor import WorldCor
from droplet import Droplet
from evocam import EvoCam

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
syringe1 =  Syringe( evobot, SYRINGES['SYRINGE1'])
#setting speed for head
head.setSpeed(9000)
#setting speed and acceleration for syringe and plunger
syringe1.syringeSetSpeed(1500)
syringe1.syringeSetAcc(1500)
syringe1.plungerSetSpeed(288)
syringe1.plungerSetAcc(96)

if not evobot.hasHomed():
    evobot.home()
evocam=EvoCam(evobot)
redDroplet=Droplet(color='default red', lowerhsv=None,upperhsv=None,minSizemm=None,maxSizemm=None,
                   minSizePix=750,maxSizePix=2000,dataLoggerName='multitrackingred',contourColor='red')

"""
blueDroplet=Droplet(color='default blue', lowerhsv=None,upperhsv=None,minSizemm=None,maxSizemm=No            self.disconnect()
ne,
                   minSizePix=1000,maxSizePix=2000,dataLoggerName='multitrackingblue',contourColor='blue')

"""

evocam.trackDroplet(redDroplet,syringe1)
evocam.record( 'multi' , extension='.mkv')
#evocam.openWindow()

def disconnectAll():
        evocam.disconnect()
        evobot.disconnect()
        sys.exit(0)
        

def signal_handler(signal, frame):
        disconnectAll()
        print('You pressed Ctrl+C!')

signal.signal(signal.SIGINT, signal_handler)

while True:
        head.move( 38, 25 )             #this is the default position where the robot makes the droplet (x,y) 
        syringe1.syringeMove( -29 )     #this is how far the syringe moves down. This has to be adjusted to match the height between experimental layer and head (start convervative)
        syringe1.plungerPushVol( 4 )    #amount of ml to dispense
        syringe1.syringeMove( -15 )     #move syringe up and hopefully out of the way
        time.sleep( 2 )
        
        while True:
            
            #evocam.updateWindow(redDroplet)
            dropletPosition = redDroplet.getPosMM()
            if dropletPosition[0] is not None:
                
                if math.sqrt( math.pow( dropletPosition[0] - head.getX(), 2) + math.pow( dropletPosition[1] - head.getY(),2  )) < 2:
                        break
                head.move(dropletPosition[0],dropletPosition[1]) 
                    
        
        syringe1.syringeMove( -29-(head.getX()-25)*(34-29)/(93-25) ) # this is because our experimental layer is at and angle. Normally a constant would be fine. 
        syringe1.plungerPullVol( 4 )                                 # amount to absorb
        syringe1.syringeMove( -15 )                                  # move syringe out of the way
                
disconnectAll()

