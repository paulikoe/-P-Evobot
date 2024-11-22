import sys
import math
import time
sys.path.append('../api')  # Open the file api
sys.path.append('../settings')

from configuration import *
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
from syringe import Syringe



# Constants
UP = -20
DOWN = -65
MAX_VOLUME = 0.20

# Coordinates

    

class Program_1:
    def __init__(self):
        
        self.data = DataLogger()
        self.evobot = EvoBot("COM6", self.data)
        self.head = Head(self.evobot)
        self.syringe = Syringe(self.evobot, SYRINGES["SYRINGE1"])  # Viz settings - local

        self.evobot.home()
        if not self.evobot.hasHomed():
            self.evobot.home()
    

    def home(self):
        self.evobot.home()
        self.syringe.plungerSetConversion(60) #Kalibrace: # Má délku 60 mm / 1 ml objem = 60
        self.syringe.plungerMoveToDefaultPos()

    def calibration(self):
        self.syringe.plungerSetConversion(60) #Kalibrace: # Má délku 60 mm / 1 ml objem = 60
        self.syringe.plungerMoveToDefaultPos()
        
    def home_end(self):
        self.evobot.home()

    def pip_pull(self, volume):
        self.syringe.syringeMove(DOWN)
        self.syringe.plungerPullVol(volume)
        time.sleep(6)
        self.syringe.syringeMove(UP)

    def pip_push(self, volume):
        self.syringe.syringeMove(DOWN)
        self.syringe.plungerPushVol(volume)
        time.sleep(2)
        self.syringe.syringeMove(UP)

    def goal_position(self, volume,coords_goalc):
        self.head.move(*coords_goalc)
        self.pip_push(volume)

    def wash(self,coords_leftc, coords_watc):
        self.head.move(*coords_watc)
        #self.pip_pull(MAX_VOLUME)
        self.pip_pull(0.3)
        self.head.move(*coords_leftc)
        #self.pip_push(MAX_VOLUME)
        self.pip_push(0.3)
        #self.head.move(*coords_watc)

    def liquid_1(self, volume,coords_goalc,coords_beak1c):
        #print(self.coords_beak1c)
        self.head.move(*coords_beak1c) # * - Rozbalení tuplu na dvě hodnoty (x, y)
        self.pip_pull(volume)
        self.goal_position(volume,coords_goalc)

    def liquid_2(self, volume,coords_goalc,coords_beak2c):
        self.head.move(*coords_beak2c)
        self.pip_pull(volume)
        self.goal_position(volume,coords_goalc)

    def quit(self):
        self.evobot.disconnect()


    def pipette_cycle(self,volume, operation):
        """Handles multiple pipetting cycles for larger volumes than the max volume of the pipette."""
        cycles = int(volume // MAX_VOLUME)  # Full cycles
        remaining_volume = volume % MAX_VOLUME  # Remaining volume

        for _ in range(cycles):
            operation(MAX_VOLUME)

        if remaining_volume > 0:
            operation(remaining_volume)




'''
vyresit pocet opakovani pro beaker2, co kdyz jich tam bude vic? se stejnym indexem, chtit tedy zadat pocet pro dany index
'''