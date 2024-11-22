import time
import sys

sys.path.append('../api')
import dropletproperties as droplet
#sys.path.append('../calibration')
from evobot import EvoBot
from evocam import EvoCam
from datalogger import DataLogger
from syringe import Syringe
from head import Head

usrMsgLogger = DataLogger()
evobot = EvoBot("/dev/tty.usbmodemfd121", usrMsgLogger)

counter=0
lastRunTime=0


head = Head( evobot )
syringe =  Syringe( evobot, 9)
syringe.plungerSetConversion( 1) #ml per mm of displacement of plunger
evobot.home()
syringe.syringeMove( -30 )

evocam=EvoCam( [[140,40,40],[180,255,255]],2000,8000, 1, '../calibration/camera-calibration.npy')

dataLogger = DataLogger( 'droplet-postion.dat')
evocam.setDataLogger( dataLogger )
evocam.windowOpen()

while True:
    try:
        #get fuel
        #head.move(20,100)
        #syringe.syringeMove( -20 )
        #syringe.plungerMovePos( 5 )
        #syringe.syringeMove( 0 )

        #move to location of droplet
        [frameNr,x,y] = evocam.getDropletPos()
        #velocityP,velocityM=evocam.getDropletVelocity(frameNr-1,frameNr)
        evocam.windowUpdate()
        
        
        #head.moveContinously( x, y)
        #if frameNr >80 and evocam.isMobile(.5, 1) is True:
        if frameNr >80 and evocam.isMobile(4, 3) is True:
            head.move( x, y)
        """
        [frameNr,x,y] = evocam.getDropletPos()
        if frameNr >80 and evocam.isStatic(.5, 1) is True:
        #if frameNr >80 and evocam.isStatic(.15, 10) is True:
            
            
            if frameNr-lastRunTime>300:
                runNumber=0
            
            
            if runNumber==0:
                
                
                head.move( x, y)
                syringe.syringeMove( -20 )
                syringe.plungerMovePos( 5 )
                syringe.syringeMove( 0 )                  
                runNumber+=1
                lastRunTime=frameNr            
                       
            
         """
            
            #counter+=1
        #if counter==100:
        
            

        

        #syringe.syringeMove( -20 )
        #syringe.plungerMovePos( 5 )
        #syringe.syringeMove( 0 )


    except KeyboardInterrupt:
        break;
        pass

evobot.disconnect()
evocam.disconnect()
