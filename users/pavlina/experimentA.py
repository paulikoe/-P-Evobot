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
import os
from ExpACoordinates import *       #Import the coordinates of the experiment 

#Positions of the vessels 
WasteVessel = 'beakerA' #change the wastevessel in the future if I want to
heightWasteVessel = -40 
heightFood1Vessel = -60 
heightMFCs = -20 

food1Volume = 5
airVolume = 3

class ExperimentA(): 
    
    #This is the function that you call in multipleExperiments, line 33
    #The syringes and modules should match
    #self: python stuff, just ignore it
    #evobot: the robot variable that you have created in multipleExperiments
    #head: the head that you have created in multipleExperiments
    #syringe0: the syringe that you have created in multipleExperiments and that it will be used in this experiment
    #expA = ExperimentA(evobot, head, syringe0)
    def __init__(self, evobot, head, syringe0):
        self.name = "ExperimentA" #Name of the experiment (used in the log)
        self.evobot = evobot
        self.head = head
        self.startTime = datetime.datetime.now()
        self.folder = "log/"
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.logFile = self.folder + self.name + '_log-{}.csv'.format(self.startTime.strftime("%Y-%m-%d %H.%M.%S"))
    
        
        #Add the syringes and the modules to some variables that can be used in 
        #all fuctions in this file. To do that, we add the "self." 
        #Now, as an example, you can use self.syringe0 everywhere in this file
        self.syringe0 = syringe0
        
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
        self.head.moveToCoord(expACoord[ WasteVessel ]) #see above the #Positions of the vessels
        #home the syringe
        self.syringe0.home()
     
        
        #Remove the liquid from the syringe)
        self.syringe0.syringeMove(heightWasteVessel) #Move the syringe down
        self.syringe0.plungerMoveToDefaultPos() #Move the plunger down to remove all the liquid
        self.syringe0.syringeMove(0) #Move the syringe up
        
        #register the feeding into the schedule
        #This function (feedMFCs) will be called every day at 13:30
        #schedule.every().day.at("13:30").do(self.feedMFCs)
        #This function (hydrateMFC1) will be called every 10 seconds (to debug)
        schedule.every(50).minutes.do(self.feedMFCs)
        #schedule.every().day.at("13:30").do(self.feedMFCs)

        #Examples to schedule tasks, replace job with your function 
#        schedule.every(10).minutes.do(job)
#        schedule.every().hour.do(job)
#        schedule.every().day.at("10:30").do(job)
#        schedule.every().monday.do(job)
#        schedule.every().wednesday.at("13:15").do(job)
        
    def update(self):
        print self.name + ": update" #Comment later, just to debug the code...
        schedule.run_pending()

################################################################################
#         Function that feeds the MFCs, it is called every day                 #
################################################################################
    def feedMFCs(self):
        functionName = "Feeding MFCs"
        print functionName
        self.log(functionName)
        
        #Prepare the recipe
        #TODO
        
        #Lets feed the nine MFCs using a loop:
        #i will vary nine times, from 0 to 8 
        for i in range(9):
            #create a string with the name of the mfc, add a one to i 
            #to get the names from 1 to 9
            name = "mfc" + str(i+1)  
            print "We have created a variable called: ", name
            self.feedOneMFC(name)
        
        #Return to park position
        self.head.moveToCoord(expACoord['beakerC'])

    def feedOneMFC(self, name):
        #Lets print what we are doing
        print self.name, ": Feeding ", name
        #absorb some food for the MFC
        self.head.moveToCoord(expACoord['beakerA'])
#        self.syringe0.plungerPullVol( airVolume )   #Absorb some air
#        self.syringe0.syringeMove(heightFood1Vessel) #Move the syringe down
#        self.syringe0.plungerPullVol( food1Volume )   #Absorb some food
#        self.syringe0.syringeMove(0) #Move the syringe up
       

#        #Dispense the food in the MFC
        self.head.moveToCoord(expACoord[name])
#        self.syringe0.syringeMove(heightMFCs) #Move the syringe down
#        self.syringe0.plungerPushVol( airVolume + food1Volume)   #Dispense food
#        self.syringe0.syringeMove(0) #Move the syringe up
#        


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
