import time
import sys
import random

sys.path.append('../api')
sys.path.append('../settings')

from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from pump import Pump
from configuration import *

class DrinkMixer:
    def __init__(self):
        self.usrMsgLogger = DataLogger()
        self.evobot = EvoBot(PORT_NO, self.usrMsgLogger)
        self.head = Head( self.evobot )
        self.syringe =  Syringe( self.evobot, SYRINGES['SYRINGE1'] )
        self.pumpSyringe =  Syringe( self.evobot, SYRINGES['SYRINGE2'] )

        self.head.setSpeed(9000)
        self.syringe.syringeSetSpeed(500)
        self.syringe.syringeSetAcc(500)
        self.syringe.plungerSetSpeed(288)
        self.syringe.plungerSetAcc(96)
        self.pumpSyringe.syringeSetSpeed(500)
        self.pumpSyringe.syringeSetAcc(500)
        self.pumpSyringe.plungerSetSpeed(288)
        self.pumpSyringe.plungerSetAcc(96)

        if not self.evobot.hasHomed():
            self.evobot.home()
        else:
            self.syringe.syringeMove( 0 )
            self.pumpSyringe.syringeMove( 0 )

        self.syringe.plungerMoveToDefaultPos()
        self.pumpSyringe.plungerMoveToDefaultPos()

    def serve( self, liquids ):
        # sum = 0
        # for i in range(0,5):
        #     sum = sum + liquids[i]
        # for id in range(0,5):
        #     amount = round( float(44.0*liquids[id]/sum), 2)
        #     if amount>1:
        #         self.getLiquidID( id, amount )
        self.addWater()

    def addWater( self ):
        self.head.move( 70, 50 )
        self.pumpSyringe.syringeMove( -48 )
        self.pumpSyringe.plungerPullVol(5)
        self.pumpSyringe.syringeMove( 0 )

        self.head.move( 150, 15 )
        self.pumpSyringe.syringeMove( -48 )
        self.pumpSyringe.plungerPushVol(5)
        self.pumpSyringe.syringeMove( 0 )

    def getLiquid( self, x, y ,amount ):
        # get liquid
        self.head.move( x, y )
        self.syringe.syringeMove( -48 )
        self.syringe.plungerPullVol( amount ) 
        self.syringe.syringeMove( 0 )

        # dispense liquid
        self.head.move( 95, 15 )
        self.syringe.syringeMove( -48 )
        self.syringe.plungerPushVol( amount ) 
        self.syringe.syringeMove( 0 )

    def getLiquidID ( self, id ,amount ):
        # get liquid
        positions=[[170,215],[95,215],[20,215],[130,135],[55,135]]
        self.getLiquid( positions[id][0], positions[id][1], amount )

    def quit(self):
        self.evobot.disconnect()

if __name__ == "__main__":    
    print "enter a number 1-5 (press any other number to quit):"
    drinkID = int(sys.stdin.readline())
    drinkmixer = DrinkMixer()
    if drinkID >= 0 and drinkID < 5:
        drinkmixer.getLiquidID( drinkID, 44 )
    elif drinkID == 5:
        #mystery drink
        sum = 0.0
        liquids = []
        for i in range(0,5):
            liquids.append( random.random() )
        drinkmixer.serve( liquids )
    else:
        drinkmixer.quit()
        sys.exit(-1)


    drinkmixer.quit()
