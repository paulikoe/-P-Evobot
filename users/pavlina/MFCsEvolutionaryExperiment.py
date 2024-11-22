import sys
sys.path.append('../../api')
sys.path.append('../../settings')


import datetime
import math
import time
import numpy as np

from head import Head

from pump import Pump
from syringe import Syringe
from worldcor import WorldCor
from datalogger import DataLogger
from evobot import EvoBot
from petridish import PetriDish

import os
from dispenser import Dispenser
from powerOutputs import PowerOutputs

from configuration import *

from agilent import Agilent
import schedule

#Import vessels and MFCs coordenates
from ExpACoordinates import expACoord
from ExpBCoordinates import expBCoord
from ExpCCoordinates import expCCoord



EXPERIMENT_TIME = 10 #24*60*60  # in seconds

# Name for the datalogger
fileName = time.strftime("%Y-%m-%d %H%M%S")


#TODO: Adjust these constants properly
S_PER_ML = 20 # Seconds per ml to use with peristaltic pumps
ML_TO_FEED_EACH_MFC = 10 #ml used to feed each MFC
SAFETY_FACTOR = 1.5



class MFCsEvolutionaryExperiment:
    """ MFCs Evolutionary experiment class, it has functions for performing evolutionary experiments with
     MFCs """

    def __init__(self, NUM_REPLICA):
        self.NUM_REPLICA = NUM_REPLICA
        self.VOL_TO_PREPARE = NUM_REPLICA * ML_TO_FEED_EACH_MFC * SAFETY_FACTOR
        """Init function used to initialize all the variables"""
        self.usrmsglogger = DataLogger()
        self.evobot = EvoBot(PORT_NO, self.usrmsglogger)
        self.head = Head(self.evobot)
        self.headLogger = DataLogger('experiments/head' + fileName, kind='csv')
        self.head.setSpeed(7000)

        #Agilent scan
        self.agilent = Agilent()



        #TODO: Initialise the modules used in the MFCs experiment

        #Dispenser module
        self.dispensing_module = Dispenser(self.evobot, SYRINGES['SYRINGE0'])
        self.dispensing_module.home_dispenser()


        # pump for reagent 1 (stepper pump)
        self.reagent1_pump = Pump(self.evobot, PUMPS['PUMP1'])
        self.reagent1_pump.setSpeed(100)

        # pumps for reagents 2, 3, and water (DC pumps)
        self.powerOutputs = PowerOutputs(self.evobot)

        # 20ml syringe
        self.big_syringe = Syringe(self.evobot, SYRINGES['SYRINGE1'])
        self.big_syringe.plungerSetSpeed(200) # Set the speed of the plunger
        self.big_syringe.plungerSetAcc(96) # Set the acc of the plunger
        self.big_syringe.syringeSetSpeed(200) # Set the speed of the syringe
        self.big_syringe.syringeSetAcc(200) # Set the acc of the syringe

        self.big_syringe.home() #Home the syringe

        # Home the head
        self.head.home()

        #TODO: This moves the plunger down, if there is liquid in the syringe, it will be dispensed.
        #TODO: Maybe it is a good ide to move the head to a waste container before this line.
        self.big_syringe.plungerMoveToDefaultPos()

    # Useful functions to dispense with peristaltic pumps
    def dispense_reagent2(self, ml):
        self.powerOutputs.turnOnD8(ml*S_PER_ML)

    def dispense_reagent3(self, ml):
        self.powerOutputs.turnOnD9(ml*S_PER_ML)

    def dispense_water(self, ml):
        self.powerOutputs.turnOnD10(ml*S_PER_ML)

    def dispense_reagent1(self, ml):
        self.reagent1_pump.pumpPushVol(5)

    #TODO: check this function
    def feed_MFCs(self, population, generation):
        """"This function feeds the MFCs based on the recipes codified in the population"""

        print "Feeding MFCs of generation " + str(generation)
        global individual_number
        for index, ind in enumerate(population):
            # For each individual (or recipe)

            reagent1, reagent2, reagent3 = ind

            # Prepare the solution to test
            # TODO: implement this
            # Example:
            self.head.moveToCoord(expACoord['beakerA']) #You need to change for each recipe or clean them!
            self.dispense_reagent1(reagent1 * self.VOL_TO_PREPARE)
            self.dispense_reagent2(reagent2 * self.VOL_TO_PREPARE)
            self.dispense_reagent3(reagent3 * self.VOL_TO_PREPARE)

            for replica in range(self.NUM_REPLICA):
                # For each replica

                print "Feeding recipe number " + str(index) + ", replica " + str(replica)
                # TODO: implement this:
                # Example:
                # Aspirate the liquid
                self.head.moveToCoord(expACoord['beakerA'])# This should match the beaker where the recipe has been made
                self.big_syringe.syringeMove(-30)   # Move the syringe down
                self.big_syringe.plungerPullVol(ML_TO_FEED_EACH_MFC) # Aspirate liquid
                self.big_syringe.homeSyringe() # Move syringe to 0

                # Choose the MFC, this tests the first individual in MFCs 0, 1 and 2;
                # the next individual in MFCs 3, 4, 5, the next one in MFCs 6, 7 and 8; and so on
                # This is important. It must match with the order used in the evaluate function
                mfc_num = index * self.NUM_REPLICA +  replica
                nameMFC = "mfc" + str(mfc_num + 1)
                self.head.moveToCoord(expACoord[nameMFC])
                self.big_syringe.syringeMove(-30)  # Move the syringe down
                self.big_syringe.plungerPushVol(ML_TO_FEED_EACH_MFC)  # Dispense liquid
                self.big_syringe.homeSyringe()  # Move syringe to 0


                # TODO: check this function
        print "Finished the feeding of all the MFCs"

    def sampleMFCs(self):
        #This is to use the simulator, use the other one for real experiments
        new_samples = self.agilent.fakeAgilentScan()
        #new_samples = self.agilent.agilentScan()

        if new_samples is not None:
            self.voltage_samples.append(new_samples)
        else:
            print "Error, agilent scanner did not sample correctly. Check that it is connected!"


    def evaluate_MFCs(self, population, generation):
        """ This function evaluates the performance of each individual (recipe) tested in a number of replicas.
        It must return the fitness ordered in the same order as the individual vector.
        """

        print "Evaluating the MFCs, recording voltages."
        #Delete previous samples
        self.voltage_samples = []

        #This line is for testing the simulator (samples every 2 seconds), use the other for real experiments
        schedule.every(2).seconds.do(self.sampleMFCs)
        #schedule.every(3).minutes.do(self.sampleMFCs)


        fitness = []

        start_time = time.time()

        while (time.time() - start_time) < EXPERIMENT_TIME:
            schedule.run_pending()

        # The experiment has finished, calculate the fitness

        #Calcualte the mean voltage for each MFC
        MFCs_voltages = np.mean(self.voltage_samples, axis = 0)
        print MFCs_voltages

        #The fitness for each individual is the mean of some replicas (NUM_REPLICA)
        for i in range(len(population)):
            start_index = i * self.NUM_REPLICA
            end_index = start_index + self.NUM_REPLICA
            print "start_index " +str(start_index) + "end_index " + str(end_index)
            fit = np.mean(MFCs_voltages[start_index:end_index])
            fitness.append(fit)

        print "Fitness calculated."
        print fitness
        print ""
        return fitness
