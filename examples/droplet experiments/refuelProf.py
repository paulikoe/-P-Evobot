import time
import sys
sys.path.append('../api')
import dropletproperties as droplet
from evobot import EvoBot
from evocam import EvoCam
from datalogger import DataLogger
from syringe import Syringe
from head import Head
import threading
from dropletTools import setupWindowSliders
import cv2



usrMsgLogger = DataLogger()
evobot = EvoBot("/dev/tty.usbmodemfd121", usrMsgLogger)


lastRunTime=0
runNumber=0


head = Head( evobot )
syringe =  Syringe( evobot, 9)
syringe.plungerSetConversion( 1) #ml per mm of displacement of plunger
evobot.home()
syringe.syringeMove( -30 )

evocam=EvoCam( [[140,40,40],[180,255,255]],3000,8000,1, '../calibration/camera-calibration.npy')

#dataLogger = DataLogger( 'droplet-postion.dat')
#evocam.setDataLogger( dataLogger )
#setupWindowSliders()
evocam.windowOpen()

def experiment():
    
    global lastRunTime, runNumber
    head.move( 20, 100 )
    syringe.syringeMove( -30 )
    syringe.plungerPullVol( 5 ) 
    #syringe.syringeMove( 0 )   
    
    

    while True:
        try:
            #get fuel
            #head.move(20,100)
            #syringe.syringeMove( -20 )
            #syringe.plungerMovePos( 5 )
            #syringe.syringeMove( 0 )

            #move to location of droplet
            #[frameNr,x,y] = evocam.getDropletPos()
            #velocity=evocam.getDropletVelocity()
            





            #if frameNr >20 and evocam.isMobile(.5, 1) is True:
             #   head.move( x, y)
              #  syringe.syringeMove( -30 )
            
            
            [frameNr,x,y] = evocam.getDropletPos()
            if frameNr >20 and evocam.isStatic(.5, 4) is True:

                if frameNr-lastRunTime>300:
                    runNumber=0


                if runNumber==0:


                    head.move( x+20, y+20)
                    syringe.syringeMove( -35 )
                    syringe.plungerPushVol( 5 )
                    syringe.syringeMove( -10 )              
                    runNumber+=1
                    lastRunTime=frameNr
                    head.move( x+40, y+40)





        except KeyboardInterrupt:
            break;
            pass

def run():
    

    t = threading.Thread(target=experiment)
    t.start()
    
    
    while True:
    
    
        print "window update"
        evocam.windowUpdate()
        
    
    
    evobot.disconnect()
    evocam.disconnect()



#--------------------------
#         main
#--------------------------
run()