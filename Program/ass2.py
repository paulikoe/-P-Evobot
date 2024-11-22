import sys
sys.path.append('../api') #open the file api 
sys.path.append('../settings')
from configuration import *
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
from syringe import Syringe

from index_coordinate import index_coordinate_1
coords_leftc, coords_watc, coords_goalc, coords_beak1c, coords_beak2c = index_coordinate_1()

class Program_2:
    def __init__(self):
        self.data = DataLogger()
        self.evobot = EvoBot("COM5", self.data)
        self.head = Head(self.evobot)
        self.syringe = Syringe(self.evobot,SYRINGES["SYRINGE1"]) #viz settings - local

        self.evobot.home()
        if not self.evobot.hasHomed():
            self.evobot.home()

'''
Z jednoho roztoku do mnoha 
'''