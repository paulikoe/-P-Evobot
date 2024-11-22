import time
import sys

sys.path.append('../../api')
sys.path.append('../../settings')
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from scale_kern_pcb import Scale
from configuration import *
import numpy as np
import csv

petridishPosx,petridishPosy=120, 210
petridishHeight = -25 #needle:-60, pipetteTip: -25
scalePosx,scalePosy=120,75
scaleHeight = -22 #needle:-70, pipetteTip: -35

liquidtoAbsorb=10
airVolume=2.0
maxIter = 30
liquidtoDespense=liquidtoAbsorb+airVolume


MM_ML_CONV_FACTOR_1ML = 58.26656956
MM_ML_CONV_FACTOR_5ML = 8.276432857
MM_ML_CONV_FACTOR_20ML = 3.145148608


scale = Scale(SCALE_PORT_NO)
usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
syringe = Syringe(evobot, SYRINGE0)
evobot.home()

head.move( petridishPosx, petridishPosy )
syringe.plungerSetSpeed(200)
syringe.plungerSetAcc(72)
syringe.syringeSetSpeed(100)
syringe.syringeSetAcc(100)
syringe.plungerMoveToDefaultPos()
syringe.plungerPullVol( 1 ) #Avoid problem rounding floats
syringe.plungerSetConversion( MM_ML_CONV_FACTOR_20ML ) #ml per mm of displacement of plunger
head.setSpeed(9000)

syringeSize ="20ml"
needle = "n170"
message = "Condtions: syringe: " + syringeSize + "needle: " + needle +" liquidtoAbsorb: " + str(liquidtoAbsorb) + "airVolume: " +str(airVolume)

file_name = syringeSize + "_" + str(liquidtoAbsorb) + str("_") + str(airVolume) + str("_") + needle +  '.csv'
with open(file_name, 'wb') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow([
        "iter",
        "weight",
        message,
    ])





    #evobot.syringe.plungerPush( 4 )
    measurements=[]
    for iter in range(0,maxIter):
        print "Iter: " +str(iter)
        try:



            #petri dish zone
            head.move( petridishPosx, petridishPosy )                     #move the head to petri dish      
            syringe.plungerPullVol( airVolume )        #absorb air



            syringe.syringeMove( petridishHeight )               #move the syringe to liquid
            syringe.plungerPullVol( liquidtoAbsorb )      #absorb water
            time.sleep(2)
            syringe.syringeMove( 0 )               #get the syringe out of liquid

            #scale Zone

            head.move( scalePosx, scalePosy )                    #move the head to the scale
            time.sleep(2)                                   #wait for the scale to balance and tare the balance


            #Tare scale
            previousWeight=scale.stableWeigh()

            syringe.syringeMove( scaleHeight )    
            syringe.plungerPushVol( liquidtoDespense ) #dispense the liquid and air
            syringe.syringeMove( 0 )
            time.sleep(2)
            currentWeight = scale.stableWeigh()
            m = currentWeight-previousWeight
            m=round(m, 3)
            measurements.append(m)
            print m
            
            writer.writerow([
                iter,
                m,
            ])

            head.move( petridishPosx, petridishPosy )

            time.sleep(0.1)



            #wait for the scale to balance and read the measure
        except KeyboardInterrupt:

            break


    syringe.syringeMove( 0 )
    head.move( petridishPosx, petridishPosy )                     #move the head to petri dish      
    syringe.syringeMove( petridishHeight )               #move the syringe to liquid
    syringe.plungerMoveToDefaultPos()
    syringe.syringeMove( 0 )

    print measurements
    print np.average(measurements)
    print np.std(measurements)
    
    writer.writerow([
                "average: ",
                np.average(measurements),
            ])
    writer.writerow([
                "std: ",
                np.std(measurements),
            ])
scale.quit()
evobot.disconnect()
