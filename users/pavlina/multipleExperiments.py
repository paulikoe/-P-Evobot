__author__ = "anfv"
__date__ = "$12-Jan-2011 18:35:37$"

import time 
import sys
sys.path.append('../../api')
sys.path.append('../../settings')
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from configuration import *
import matplotlib.dates as mdates
from powerOutputs import PowerOutputs

#Import the experiment classes:
#from experimentA import ExperimentA
from experimentB import ExperimentB
from experimentC import ExperimentC
from agilent import Agilent
import Queue
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm


#Create the evobot class
usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )
powerOutputs = PowerOutputs( evobot)

#create the syringe that all these experiments will use
#syringe0 = Syringe(evobot, SYRINGES['SYRINGE0'])   #Experiment A
syringe12 = Syringe(evobot, SYRINGES['SYRINGE12']) #Experiment B
syringe16 = Syringe(evobot, SYRINGES['SYRINGE16']) #Experiment C

#Create the dispensing module as a syringe (Experiments A and B)
dispensingModule = Syringe(evobot, SYRINGES['SYRINGE7'])   #Experiment B and C

#Create all the experiments
#expA = ExperimentA(evobot, head, syringe0) 
expB = ExperimentB(evobot, head, syringe12, dispensingModule,powerOutputs)
expC = ExperimentC(evobot, head, syringe16, dispensingModule,powerOutputs)

expBQueue = Queue.Queue()
expCQueue = Queue.Queue()

agilent = Agilent(expBQueue, expCQueue)

#Add the experiments to the experiments list
#expList = [expA, expB, expC]
expList = [expB, expC, agilent]

#debug agilent***
#expList = [agilent]

#The syringes have to be defined inside each experiment



timeVectorB = []
timeVectorC = []
mfc1Vector = []
mfc2Vector = []
mfc3Vector = []
mfc4Vector = []
mfc5Vector = []
mfc6Vector = []
mfc7Vector = []
mfc8Vector = []
mfc9Vector = []
mfc10Vector = []
mfc11Vector = []
mfc12Vector = []
mfc13Vector = []
mfc14Vector = []
mfc15Vector = []
mfc16Vector = []
mfc17Vector = []
mfc18Vector = []


myFmt = mdates.DateFormatter('%d')
figExpB = plt.figure("Experiment B")
axExpB = figExpB.add_subplot(111)
figExpC = plt.figure("Experiment C")
axExpC = figExpC.add_subplot(111)
colors = cm.rainbow(np.linspace(0, 1, 9))
#li, = ax.plot(timeVector, y)
# draw and show it
figExpB.canvas.draw()
figExpC.canvas.draw()
plt.show(block=False)

"""
Setup the experiments
"""
#Home the head
evobot.home()



#Call the setup function for each experiment, they will home their modules #4loop
for exp in expList:
    exp.setup()

"""
Run the experiments
"""
while True:
    try:
        for exp in expList:
            exp.update()
        
        while not expBQueue.empty():
            tB, mfc1, mfc2, mfc3, mfc4, mfc5, mfc6, mfc7, mfc8, mfc9= expBQueue.get()
            timeVectorB.append(tB)
            mfc1Vector.append(mfc1)
            mfc2Vector.append(mfc2)
            mfc3Vector.append(mfc3)
            mfc4Vector.append(mfc4)
            mfc5Vector.append(mfc5)
            mfc6Vector.append(mfc6)
            mfc7Vector.append(mfc7)
            mfc8Vector.append(mfc8)
            mfc9Vector.append(mfc9)
            
        while not expCQueue.empty():
            tC, mfc10, mfc11, mfc12, mfc13, mfc14, mfc15, mfc16, mfc17, mfc18= expCQueue.get()
            timeVectorC.append(tC)
            mfc10Vector.append(mfc10)
            mfc11Vector.append(mfc11)
            mfc12Vector.append(mfc12)
            mfc13Vector.append(mfc13)
            mfc14Vector.append(mfc14)
            mfc15Vector.append(mfc15)
            mfc16Vector.append(mfc16)
            mfc17Vector.append(mfc17)
            mfc18Vector.append(mfc18)
        
        axExpB.cla()
        axExpB.plot(timeVectorB, mfc1Vector, color=colors[0], linewidth=1, label="MFC1")
        axExpB.plot(timeVectorB, mfc2Vector, color=colors[1], linewidth=1, label="MFC2")
        axExpB.plot(timeVectorB, mfc3Vector, color=colors[2], linewidth=1, label="MFC3")
        axExpB.plot(timeVectorB, mfc4Vector, color=colors[3], linewidth=1, label="MFC4")
        axExpB.plot(timeVectorB, mfc5Vector, color=colors[4], linewidth=1, label="MFC5")
        axExpB.plot(timeVectorB, mfc6Vector, color=colors[5], linewidth=1, label="MFC6")
        axExpB.plot(timeVectorB, mfc7Vector, color=colors[6], linewidth=1, label="MFC7")
        axExpB.plot(timeVectorB, mfc8Vector, color=colors[7], linewidth=1, label="MFC8")
        axExpB.plot(timeVectorB, mfc9Vector, color=colors[8], linewidth=1, label="MFC9")
        axExpB.set_xlabel('Date')
        axExpB.set_ylabel('Voltage')
        axExpB.legend(loc='upper left')
        figExpB.autofmt_xdate()
        figExpB.canvas.draw()
        plt.pause(0.5)
        
        axExpC.cla()
        axExpC.plot(timeVectorC, mfc10Vector, color=colors[0], linewidth=1, label="MFC10")
        axExpC.plot(timeVectorC, mfc11Vector, color=colors[1], linewidth=1, label="MFC11")
        axExpC.plot(timeVectorC, mfc12Vector, color=colors[2], linewidth=1, label="MFC12")
        axExpC.plot(timeVectorC, mfc13Vector, color=colors[3], linewidth=1, label="MFC13")
        axExpC.plot(timeVectorC, mfc14Vector, color=colors[4], linewidth=1, label="MFC14")
        axExpC.plot(timeVectorC, mfc15Vector, color=colors[5], linewidth=1, label="MFC15")
        axExpC.plot(timeVectorC, mfc16Vector, color=colors[6], linewidth=1, label="MFC16")
        axExpC.plot(timeVectorC, mfc17Vector, color=colors[7], linewidth=1, label="MFC17")
        axExpC.plot(timeVectorC, mfc18Vector, color=colors[8], linewidth=1, label="MFC18")
        axExpC.set_xlabel('Date')
        axExpC.set_ylabel('Voltage')
        axExpC.legend(loc='upper left')
        figExpC.autofmt_xdate()
        figExpC.canvas.draw()
        plt.pause(0.5)

        #plt.pause(0.001)
        
    except KeyboardInterrupt:
        break
        
