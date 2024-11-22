__author__ = "anfv"
__date__ = "$29-Sep-2016 11:35:37$"

import time 
import sys
sys.path.append('../../api')
sys.path.append('../../settings')
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from configuration import *

#Import the experiment classes:
from experimentA import ExperimentA
from experimentB import ExperimentB

#Create the evobot class
usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot )

#Create all the experiments
expA = ExperimentA(evobot, head)
expB = ExperimentB(evobot, head)

#Add the experiments to the experiments list
expList = [expA, expB]



#The syringes have to be defined inside each experiment

"""
Setup the experiments
"""
#Home the head
evobot.homeHead()

#Call the setup function for each experiment, they will home their modules
for exp in expList:
    exp.setup()

"""
Run the experiments
"""
while True:
    try:
        for exp in expList:
            exp.update()
            time.sleep(1)

    except KeyboardInterrupt:
        break
        
