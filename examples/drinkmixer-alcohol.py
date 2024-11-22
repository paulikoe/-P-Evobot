import time
import sys

sys.path.append('../api')
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head

usrMsgLogger = DataLogger()
evobot = EvoBot("/dev/tty.usbmodem1421", usrMsgLogger)
head = Head( evobot )
headLogger = DataLogger( 'experiments/head.dat')
syringe =  Syringe( evobot, 1 )
syringeLogger = DataLogger( 'experiments/syringe.dat')
syringe.plungerSetConversion( 1 ) #ml per mm of displacement of plunger

head.dataLogger = headLogger
syringe.dataLogger = syringeLogger

evobot.home()

syringe.plungerMoveToDefaultPos()        

head.move( 65, 88 )
syringe.syringeMove( -65 )
syringe.plungerPullVol( 15 ) 
syringe.syringeMove( -10 )

# dispense liquid 
head.move( 60, 150 )
syringe.syringeMove( -30 )
syringe.plungerPushVol( 15 ) 
syringe.syringeMove( -10 )

head.move( 130, 88 )
syringe.syringeMove( -65 )
syringe.plungerPullVol( 15 ) 
syringe.syringeMove( -10 )

# dispense liquid 
head.move( 60, 150 )
syringe.syringeMove( -30 )
syringe.plungerPushVol( 15 ) 
syringe.syringeMove( -10 )

# destroy earth
evobot.disconnect()
