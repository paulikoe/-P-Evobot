import sys
sys.path.append('../api') #open the file api 
sys.path.append('../settings')
from configuration import *
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
from syringe import Syringe

data = DataLogger()
evobot = EvoBot("COM5", data)
head = Head(evobot)
syringe = Syringe(evobot,SYRINGES["SYRINGE1"]) #viz settings - local
#syringe.plungerSetConversion
evobot.home()
if not evobot.hasHomed():
    evobot.home()

syringe.plungerSetConversion(1) #mm per ml #mm = ml * factor --> factor = 1mm/0.1 ml
#syringe.plungerMoveToDefaultPos()

i = 0
while i<1:
    try:
        head.move(0,200)
        syringe.syringeMove(-65)
        syringe.plungerPullVol(5) #5mm
        #syringe.syringeMove(0)
    except KeyboardInterrupt:
        break

    i += 1