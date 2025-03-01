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
import os
from ExpBCoordinates import *
from powerOutputs import PowerOutputs

# Setting position of the vessels
Food1Vessel = 'beakerE'
Food2Vessel = 'beakerD'
heightFood1Vessel = -60
heightFood2Vessel = -60
heightMFCs = -35
foodVolume = 20 #3.5mm = 1 ml
airVolume = 5

class ExperimentB(): 
    def __init__(self, evobot, head, syringe, dispensingModule,powerOutputs):
        self.name = "ExperimentB"
        self.evobot = evobot
        self.head = head
        self.powerOutputs =powerOutputs
        self.startTime = datetime.datetime.now()
        self.folder = "log/"
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.logFile = self.folder + self.name + '_log-{}.csv'.format(self.startTime.strftime("%Y-%m-%d %H.%M.%S"))
    
        #Create the log of the experiment
        with open(self.logFile , 'wb') as f:
            self.writer = csv.writer(f, delimiter=',')
            self.writer.writerow([
                'Day',
                'Time',
                'Function',
            ])
            
        #Add the syringes and the modules to some variables that can be used in 
        #all fuctions in this file. To do that, we add the "self." 
        #Now, as an example, you can use self.syringe12 everywhere in this file
        self.syringe12 = syringe
        self.dispensingModule = dispensingModule
        
    def setup(self):
        print self.name + ": setup"
        
        #home the syringe
        self.syringe12.home()
        self.dispensingModule.home()
        
        #register the feeding into the schedule
        schedule.every(1).days.at("16:00").do(self.feedMFCs)
        #schedule.every(10).seconds.do(self.feedMFCs)
        #schedule.every(2).minutes.do(self.feedMFCs)
       
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
        
##    def feedMFC2(self):
##        functionName = "Feeding MFC2"
##        print functionName
##        self.log(functionName)
        
    def feedMFCs(self):
        
        functionName = "Feeding MFCs Exp. B"
        print functionName
        self.log(functionName)
        self.head.home()
        self.syringe12.home()
        self.dispensingModule.home()
        self.syringe12.syringeMove(-20)
        # 50 ml is 140 seconds
        self.feedBeaker('dispBeakerE',35)
        self.feedBeaker('dispBeakerE',35)
        self.feedBeaker('dispBeakerE',35)
        self.feedBeaker('dispBeakerE',35)
        
        self.feedBeaker('dispBeakerD',35)
        self.feedBeaker('dispBeakerD',35)
        self.feedBeaker('dispBeakerD',35)
        self.feedBeaker('dispBeakerD',35) 
		# Order and list of MFC feeds
		# E to 1 & 2
	self.feedOneMFC('beakerE','mfc1')
	self.feedOneMFC('beakerE','mfc2')
	self.feedOneMFC('beakerE','mfc3')
	self.feedOneMFC('beakerE','mfc4')
	self.feedOneMFC('beakerE','mfc5')
	self.feedOneMFC('beakerD','mfc6')
	self.feedOneMFC('beakerD','mfc7')
	self.feedOneMFC('beakerD','mfc8')
	self.feedOneMFC('beakerD','mfc9')
	print 'Experiment B feed'
        #Return to park position
        self.head.moveToCoord(expBCoord['park'])
		
    def feedOneMFC(self, source, dest):
  	self.syringe12.plungerMoveToDefaultPos()      
        self.head.moveToCoord(expBCoord[source])
        self.syringe12.plungerPullVol( airVolume )   #Absorb some air
        self.syringe12.syringeMove(heightFood1Vessel) #Move the syringe down
        #Mix 3 times
        self.syringe12.plungerPullVol( foodVolume ) #1
        self.syringe12.plungerPushVol( foodVolume)
        self.syringe12.plungerPullVol( foodVolume ) #2
        self.syringe12.plungerPushVol( foodVolume)
        self.syringe12.plungerPullVol( foodVolume ) #3
        self.syringe12.plungerPushVol( foodVolume)
        #Feeder
        self.syringe12.plungerPullVol( foodVolume )   #Absorb some food
        self.syringe12.syringeMove(-20) #Move the syringe up
                    #Dispense the food in the MFC
        time.sleep(1)
        self.head.moveToCoord(expBCoord[dest])
        self.syringe12.syringeMove(heightMFCs) #Move the syringe down
        self.syringe12.plungerPushVol( airVolume + foodVolume)   #Dispense food
        self.syringe12.syringeMove(-20) #Move the syringe up   
	#self.syringe12.home()
	time.sleep(1)
    def feedBeaker(self, dest,t_amount):
	self.head.moveToCoord(expBCoord[dest])
	self.dispensingModule.syringeMove( -70 )
	self.powerOutputs.turnOnD10()
        time.sleep(t_amount)
        self.powerOutputs.turnOffD10()
        self.dispensingModule.syringeMove( -10 )
        self.head.moveToCoord(expBCoord['park'])
	
	
	
        
        
