import time
import sys
sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from scanner import Scanner
from head import Head

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
scanner =  Scanner( evobot, SCANNERS['SCANNER1'])
evobot.home()

while True:
    try:
        head.move( 20, 100 )
        scanner.scannerMovePos( 20 )

        head.move( 40, 100 )
        scanner.scannerMovePos( 21 )
        
        head.move( 60, 100 )
        scanner.scannerMovePos( 22 )     
        
        head.move( 40, 100 )
        scanner.scannerMovePos( 21 )  
        
    except KeyboardInterrupt:
        break

evobot.disconnect()
