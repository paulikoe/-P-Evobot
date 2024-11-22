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
#evobot.home()


for x in range(0,30):
    try:
        
        
        evobot.send("G1 Z1" )                     
        time.sleep(8)   
        
        evobot.send("G1 Z1.5" )                     
        time.sleep(8) 
        
        evobot.send("G1 Z2" )                     
        time.sleep(8)     
        
        evobot.send("G1 Z10" )                     
        time.sleep(8)        
        
        evobot.send("G1 Z20" )                     
        time.sleep(8)
        
        evobot.send("G1 Z0" )                     
        time.sleep(8)        


    except KeyboardInterrupt:
        break

evobot.disconnect()
