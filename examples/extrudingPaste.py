import time
import sys
sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
extruder =  Syringe( evobot, SYRINGES['SYRINGE1'])
syringe =  Syringe( evobot, SYRINGES['SYRINGE2'])

#Home the extruder with the paste
extruder.homeSyringe()

#Home all the syringes, if any
#syringe.home()
#syringe.plungerMoveToDefaultPos()

#Home the head
evobot.homeHead()





#Setting the maximum speed 
#TODO: Set the maximum acc for the head
head.setSpeed(9000)
extruder.syringeSetSpeed(1500)
extruder.syringeSetAcc(1500)
extruder.plungerSetSpeed(50) 
extruder.plungerSetAcc(96)

#Move the robot to the starting position and move the syringe down
head.move( 20, 100 )
extruder.syringeMove( -30 )
extruder.plungerExtrude() 

#Move the syringe following a path
head.move( 80, 100 )
head.move( 80, 105 )
head.move( 20, 105 )
head.move( 20, 110 )
head.move( 80, 110 )
head.move( 80, 115 )
head.move( 20, 115 )

#Stop the extruding
extruder.plungerHardStop() 
#A soft stop is also available, use the most convenient
#extruder.plungerSoftStop() 


extruder.syringeMove( 0 )
head.move(0, 0)


evobot.disconnect()
