# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import schedule
import datetime
import time
import sys
sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
import csv

class ExperimentB(): 
    def __init__(self, evobot, head):
        self.name = "ExperimentB"
        self.evobot = evobot
        self.head = head
        self.startTime = datetime.datetime.now()
        self.logFile = "log/" + self.name + '_log-{}.csv'.format(self.startTime.strftime("%Y-%m-%d %H.%M.%S"))
    
        #Create the log of the experiment
        with open(self.logFile , 'wb') as f:
            self.writer = csv.writer(f, delimiter=',')
            self.writer.writerow([
                'Day',
                'Time',
                'Function',
            ])
        #create the syringe that this experiment will use
        self.syringe2 = Syringe(self.evobot, SYRINGE2)
        
    def setup(self):
        print self.name + ": setup"
        
        #home the syringe
        self.syringe2.home()
        
        #register the feeding into the schedule
        schedule.every(3).seconds.do(self.feedMFC2)
        
    def update(self):
        print self.name + ": update"
        schedule.run_pending()
    
    def log(self, functionName):
        currentTime = datetime.datetime.now()
        with open(self.logFile, 'ab') as f:
            self.writer = csv.writer(f, delimiter=',')
            self.writer.writerow([
                currentTime.strftime("%Y.%m.%d"),
                currentTime.strftime("%H.%M.%S"),
                functionName,
            ])
        
    def feedMFC2(self):
        functionName = "Feeding MFC2"
        print functionName
        self.log(functionName)
        

        
        