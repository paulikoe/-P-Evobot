import time
import sys

sys.path.append('../api')
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head

usrMsgLogger = DataLogger()
evobot = EvoBot("/dev/tty.usbmodemfd121", usrMsgLogger)




head = Head( evobot )
syringe =  Syringe( evobot, 2)
syringe.plungerSetConversion( 8.7191 ) #ml per mm of displacement of plunger
evobot.home()



petridishPosx,petridishPosy=5, 160
scalePosx,scalePosy=120,160
liquidtoAbsorb=38
liquidtoDespense=30
#airVolume=12

#evobot.syringe.plungerPush( 4 )
for x in range(0,1):
    try:

        #petri dish zone
        head.move( petridishPosx, petridishPosy )                     #move the head to petri dish
        syringe.plungerMovePos( 41 )      
#        evobot.syringe.plungerPull( airVolume )         #absorb air
        syringe.syringeMove( -47 )               #move the syringe to liquid
        syringe.plungerMovePos( 41-liquidtoAbsorb )      #absorb water
        time.sleep(5)
        syringe.syringeMove( -35 )               #get the syringe out of liquid

        #scale Zone

        head.move( scalePosx, scalePosy )                    #move the head to the scale
        time.sleep(8)                                   #wait for the scale to balance and tare the balance
        
        syringe.plungerMovePos( 41-liquidtoAbsorb+liquidtoDespense ) #dispense the liquid and air
        time.sleep(10)
        syringe.syringeMove( 0 )
        time.sleep(2)
        head.move( petridishPosx, petridishPosy ) 
        
        evobot.home()
        #wait for the scale to balance and read the measure
    except KeyboardInterrupt:
        break

evobot.disconnect()
