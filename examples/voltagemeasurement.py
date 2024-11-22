import time
import sys

sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from voltagesensor import VoltageSensor


usrMsgLogger = DataLogger()
voltageLogger = DataLogger( 'experiments/voltage', kind='dat')
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
headLogger = DataLogger( 'experiments/head', kind='dat')
syringe =  Syringe( evobot, SYRINGES['SYRINGE1'] )
syringeLogger = DataLogger( 'experiments/syringe', kind='dat')
voltagesensor = VoltageSensor( evobot, 0 )

head.dataLogger = headLogger
syringe.dataLogger = syringeLogger
voltagesensor.dataLogger = voltageLogger

evobot.home()

while True:
    syringe.plungerMoveToDefaultPos()        

    while True:
        voltage = voltagesensor.getMeasurement()
        if voltage < 1 or voltage > 4:
            break
        time.sleep(0.5)


        # get liquid A and move to MFC entry A
        if voltage > 4:
            head.move( 15, 105 )
            syringe.syringeMove( -65 )
            syringe.plungerPullVol( 5 ) 
            syringe.syringeMove( 0 )
            head.move( 148.5, 119 )

            # get liquid B and move eto MFC entry B
            if voltage < 1:
                head.move( 145, 0 )
                syringe.syringeMove( -65 )
                syringe.plungerPullVol( 5 ) 
                syringe.syringeMove( 0 )
                head.move( 156, 103 )

                # dispense liquid 
                syringe.syringeMove( -58 )
                syringe.plungerPushVol( 5 ) 
                syringe.syringeMove( 0 )

                # move to water bath and clean
                head.move( 15, 0 )
                syringe.syringeMove( -65 )
                syringe.plungerPullVol( 10 ) 
                syringe.plungerPushVol( 10 ) 
                syringe.plungerPullVol( 10 ) 
                syringe.plungerPushVol( 10 ) 
                syringe.plungerPullVol( 10 ) 
                syringe.plungerPushVol( 10 ) 
                syringe.syringeMove( 0 )
