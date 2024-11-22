import sys
import time 
sys.path.append('../api') #open the file api 
sys.path.append('../settings')
from configuration import *
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
from syringe import Syringe

data = DataLogger()
evobot = EvoBot("COM6", data)
head = Head(evobot)
syringe = Syringe(evobot,SYRINGES["SYRINGE1"]) #viz settings - local
#syringe.plungerSetConversion
#evobot.home()

if not evobot.hasHomed():
    evobot.home()

syringe.plungerSetConversion(60) #mm per ml #mm = ml * factor --> factor = 1mm/0.1 ml
#syringe.syringeMove(-65)
syringe.plungerMoveToDefaultPos()

def calibration():
        syringe.plungerSetConversion(60) #Kalibrace: # Má délku 60 mm / 1 ml objem = 60
        syringe.plungerMoveToDefaultPos()

i = 0
while i<1:
    try:
        x = (313.9203536 - 37)*2 #10 cm má jako 5
        y = (218.75983360000004 + 67)*2
        x = 313.9203536
        y = 218.75983360000004
        x1 = 10
        y1 = 30
        head.move(x1,y1)
        
        syringe.syringeMove(-65)
        calibration()
        #syringe.plungerPullVol(0.1)
        time.sleep(3) #3-4 sekundy na 0,1 ml
        syringe.syringeMove(-20)
        #head.move(255.94020799999996,19.859583999999984)
        head.move(40,30)
        syringe.syringeMove(-65)
        time.sleep(2)
        syringe.syringeMove(-20)
        time.sleep(2)
        syringe.syringeMove(-65)
        time.sleep(2)
        syringe.syringeMove(-20)
        time.sleep(2)
        syringe.syringeMove(-65)
        time.sleep(5)
        #syringe.plungerPushVol(0.1) #5mm¨
        #syringe.plungerPullVol(5)
        #evobot.home()
        
    except KeyboardInterrupt:
        break

    i += 1