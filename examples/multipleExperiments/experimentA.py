# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import schedule
import datetime
import time
import sys
sys.path.append('../../api')
sys.path.append('../../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
import csv

#Positions of the vessels 
wasteVesselx, wasteVessely = 100,0
heightWasteVessel = -40 
food1Vesselx, food1Vessely = 180,50
heightFood1Vessel = -60 
mfc1x, mfc1y = 50,100
heightMFCl = -20 

food1Volume = 5
airVolume = 3

class ExperimentA(): 
    def __init__(self, evobot, head):
        self.name = "ExperimentA"
        self.evobot = evobot
        self.head = head
        self.startTime = datetime.datetime.now()
        self.logFile = "log/" + self.name + '_log-{}.csv'.format(self.startTime.strftime("%Y-%m-%d %H.%M.%S"))
        
        #create the syringe that this experiment will use
        self.syringe0 = Syringe(self.evobot, SYRINGE0)
        
        #Create the log of the experiment
        with open(self.logFile, 'wb') as f:
            self.writer = csv.writer(f, delimiter=',')
            self.writer.writerow([
                'Day',
                'Time',
                'Function',
            ])
        
    
    def setup(self):
        print self.name + ": setup"
        #Move to the waste vessel
        self.head.move(wasteVesselx, wasteVessely)
        #home the syringe
        self.syringe0.home()
        
        #Remove the liquid from the syringe)
        self.syringe0.syringeMove(heightWasteVessel) #Move the syringe down
        self.syringe0.plungerMoveToDefaultPos() #Move the plunger down to remove all the liquid
        self.syringe0.syringeMove(0) #Move the syringe up
        
        #register the feeding into the schedule
        schedule.every(30).seconds.do(self.feedMFC1)
        schedule.every(10).seconds.do(self.hydrateMFC1)
        
        #Examples to schedule tasks, replace job with your function 
#        schedule.every(10).minutes.do(job)
#        schedule.every().hour.do(job)
#        schedule.every().day.at("10:30").do(job)
#        schedule.every().monday.do(job)
#        schedule.every().wednesday.at("13:15").do(job)
        
    def update(self):
        print self.name + ": update"
        
        schedule.run_pending()
        
    def feedMFC1(self):
        functionName = "Feeding MFC1"
        print functionName
        self.log(functionName)
        
        
        #absorb some food for the MFC
        self.head.move(food1Vesselx, food1Vessely)
#        self.syringe0.plungerPullVol( airVolume )   #Absorb some air
#        self.syringe0.syringeMove(heightFood1Vessel) #Move the syringe down
#        self.syringe0.plungerPullVol( food1Volume )   #Absorb some food
#        self.syringe0.syringeMove(0) #Move the syringe up
#        
#        #Dispense the food in the MFC
        self.head.move(mfc1x, mfc1y)
#        self.syringe0.syringeMove(heightMFCl) #Move the syringe down
#        self.syringe0.plungerPushVol( airVolume + food1Volume)   #Dispense food
#        self.syringe0.syringeMove(0) #Move the syringe up
#        
#        #Return to park position
#        self.head.move(wasteVesselx, wasteVessely)

    def hydrateMFC1(self):
        functionName = "Hydrating MFC1"
        print functionName
        self.log(functionName)
        
        
        
    def log(self, functionName):
        currentTime = datetime.datetime.now()
        with open(self.logFile, 'ab') as f:
            self.writer = csv.writer(f, delimiter=',')
            self.writer.writerow([
                currentTime.strftime("%Y.%m.%d"),
                currentTime.strftime("%H.%M.%S"),
                functionName,
            ])
