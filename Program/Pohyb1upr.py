import sys
sys.path.append('../api') #open the file api 
sys.path.append('../settings')
from configuration import *
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
from syringe import Syringe


class Program_1:
    def __init__(self):
        self.data = DataLogger()
        self.evobot = EvoBot("COM5", self.data)
        self.head = Head(self.evobot)
        self.syringe = Syringe(self.evobot,SYRINGES["SYRINGE1"]) #viz settings - local
        self.up = 0
        self.down = -65
        #newhome = (0,100) #new_home
        self.evobot.home()
        if not self.evobot.hasHomed():
            self.evobot.home()

    def pip(self,volume):
        self.syringe.syringeMove(self.down)
        #self.syringe.plungerPullVol(volume)
        self.syringe.syringeMove(self.up)
    
    def goal_position(self,x_g,y_g,volume):
        #self.evobot.home()
        self.head.move(x_g,y_g)
        self.syringe.syringeMove(self.down)
        #self.syringe.plungerPushVol(volume)
        self.syringe.syringeMove(self.up)

    def wash(self,x_w,y_w,x_w1,y_w1): #plus volume
        self.head.move(x_w1,y_w1) 
        self.pip(self.up,self.down) #plus volume
        self.head.move(x_w,y_w) #position of the beaker for leftovers
        #self.syringe.syringeMove(down)
        #self.syringe.plungerPushVol(volume)
        #self.syringe.syringeMove(up)
        self.head.move(x_w1,y_w1) 
    
    def liquid_1(self,x_l1,y_l1):
        self.head.move(x_l1,y_l1)
        self.pip()
        self.goal_position()
        self.wash()
    
    def liquid_2(self,x_l2,y_l2):
        self.head.move(x_l2,y_l2)
        self.pip()
        self.goal_position()
        self.wash()
    
    def quit(self):
        self.evobot.disconnect()

program = Program_1()
#Wash
x_w = 0
y_w = 150

x_w1 = 0
y_w1 = 200

#liquid 1
x_l1 = 100
y_l1 = 100

#liquid 2
x_l2 = 100
y_l2 = 200

#goal position
x_g = 100
y_g = 150

#volume
volume = 5 #ml

#up or down position of the syringe
up = 0
down = -60

while True:
    try:
        program.wash(x_w,y_w,x_w1,y_w1) #plus volume
        #program.liquid_1(x_l1,y_l1,volume,up,down)
        #program.liquid_2(x_l2,y_l2,volume,up,down)
    except KeyboardInterrupt:
        break

program.quit()
