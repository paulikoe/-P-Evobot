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

class Program_1:
    def __init__(self):
        self.data = DataLogger()
        self.evobot = EvoBot("COM5", self.data)
        self.head = Head(self.evobot)
        self.syringe = Syringe(self.evobot,SYRINGES["SYRINGE1"]) #viz settings - local

        #self.up = 0
        #self.down = -65

        #newhome = (0,100) #new_home
        self.evobot.home()
        if not self.evobot.hasHomed():
            self.evobot.home()

    def pip_pull(self,up,down): #plus volume
        self.syringe.syringeMove(down)
        #self.syringe.plungerPullVol(volume)
        self.syringe.syringeMove(up)

    def pip_push(self,up,down): #plus volume
        self.syringe.syringeMove(down)
        #self.syringe.plungerPushVol(volume)
        self.syringe.syringeMove(up)

    def goal_position(self,coords_goalc,up,down):
        #self.evobot.home()
        self.head.move(coords_goalc)
        self.pip_push(up,down)

    def wash(self,coords_leftc,coords_watc,up,down): #plus volume
        self.head.move(coords_watc) 
        self.pip_pull(up,down) #plus volume
        self.head.move(coords_leftc) #position of the beaker for leftovers
        self.pip_push(up,down)
        self.head.move(coords_watc) 
    
    def liquid_1(self,coords_beak1c,up,down,coords_goalc):
        self.head.move(coords_beak1c)
        self.pip_pull(up,down)
        self.goal_position(coords_goalc,up,down)
        
    
    def liquid_2(self,coords_beak2c,up,down,coords_goalc):
        self.head.move(coords_beak2c)
        self.pip_pull(up,down)
        self.goal_position(coords_goalc,up,down)
        
    
    def quit(self):
        self.evobot.disconnect()


program1 = Program_1()

#up or down position of the syringe
up = 0
down = -60
'''
coords_leftc, coords_watc, coords_goalc, coords_beak1c, coords_beak2c
i = 0
while i < 1:
    try:
        program.wash(coords_leftc,coords_watc,up,down) #plus volume
        program.liquid_1(coords_beak1c,up,down,coords_goalc)
        program.wash(coords_leftc,coords_watc,up,down)
        program.liquid_2(coords_beak2c,up,down,coords_goalc)
        #program.wash(x_w,y_w,x_w1,y_w1,up,down)
    except KeyboardInterrupt:
        break
    i += 1
''' 
program.quit()

'''

něco jako Kadinka 1 = 01 přes input uzivatel vloží 01 a pak tam bude podmínka, že hledáme souradnice pro 
01, pokud nebude nalezeno, hodí to chybu

muzu to dleat pres input, vyber si ukol 1,2,3 .. podle toho se nactou potrebne slozky ktere k ukolu potrebuju a ty se priradi do daneho souboru
'''

