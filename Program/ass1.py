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

    def goal_position(self,x_g,y_g,up,down):
        #self.evobot.home()
        self.head.move(x_g,y_g)
        self.pip_push(up,down)

    def wash(self,x_w,y_w,x_w1,y_w1,up,down): #plus volume
        self.head.move(x_w1,y_w1) 
        self.pip_pull(up,down) #plus volume
        self.head.move(x_w,y_w) #position of the beaker for leftovers
        self.pip_push(up,down)
        self.head.move(x_w1,y_w1) 
    
    def liquid_1(self,x_l1,y_l1,up,down,x_g,y_g):
        self.head.move(x_l1,y_l1)
        self.pip_pull(up,down)
        self.goal_position(x_g,y_g,up,down)
        
    
    def liquid_2(self,x_l2,y_l2,up,down,x_g,y_g):
        self.head.move(x_l2,y_l2)
        self.pip_pull(up,down)
        self.goal_position(x_g,y_g,up,down)
        
    
    def quit(self):
        self.evobot.disconnect()

#leftovers
leftc = int(input("Write index of beaker for leftovers: "))

# Načtení souboru s názvem "text"
with open("data/qr_results_new.txt", "r") as file:
    lines = file.readlines()

# Inicializace proměnných pro souřadnice
coords = None

# Prohledání řádků pro daný index
for line in lines:
    parts = line.split()
    index = int(parts[0])
    if index == leftc:
        coords = parts[1], parts[2]
        break

# Pokud jsme našli souřadnice, vypíšeme je
if coords:
    print(f"Coordinates for beaker {leftc} are: {coords[0]}, {coords[1]}")
else:
    print(f"Beaker with index {leftc} not found.")



program = Program_1()
'''
#Wash
x_w = 0
y_w = 200

x_w1 = 0
y_w1 = 400

#liquid 1
x_l1 = 100
y_l1 = 100

#liquid 2
x_l2 = 100
y_l2 = 400

#goal position
x_g = 100
y_g = 250

#volume
volume = 5 #ml
'''
#up or down position of the syringe
up = 0
down = -60


i = 0
while i < 1:
    try:
        program.wash(x_w,y_w,x_w1,y_w1,up,down) #plus volume
        program.liquid_1(x_l1,y_l1,up,down,x_g,y_g)
        program.wash(x_w,y_w,x_w1,y_w1,up,down)
        program.liquid_2(x_l2,y_l2,up,down,x_g,y_g)
        #program.wash(x_w,y_w,x_w1,y_w1,up,down)
    except KeyboardInterrupt:
        break
    i += 1
    
program.quit()

'''

něco jako Kadinka 1 = 01 přes input uzivatel vloží 01 a pak tam bude podmínka, že hledáme souradnice pro 
01, pokud nebude nalezeno, hodí to chybu

muzu to dleat pres input, vyber si ukol 1,2,3 .. podle toho se nactou potrebne slozky ktere k ukolu potrebuju a ty se priradi do daneho souboru
'''

