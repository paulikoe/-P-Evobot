# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import schedule
import datetime
import threading
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
from collections import deque
import matplotlib.pyplot as plt
import numpy as np
import time
import random
import Queue
import visa
#visa.log_to_screen()

lock = threading.Lock()
C1MFC1 = 0
C1MFC2 = 0
C1MFC3 = 0
C1MFC4 = 0
C1MFC5 = 0
C1MFC6 = 0
C1MFC7 = 0
C1MFC8 = 0
C1MFC9 = 0
C1MFC10 = 0
C1MFC11 = 0
C1MFC12 = 0
C1MFC13 = 0
C1MFC14 = 0
C1MFC15 = 0
C1MFC16 = 0
C1MFC17 = 0
C1MFC18 = 0

safeMFC1 = []
safeMFC2 = []
safeMFC3 = []
safeMFC4 = []
safeMFC5 = []
safeMFC6 = []
safeMFC7 = []
safeMFC8 = []
safeMFC9 = []
safeMFC10 = []
safeMFC11 = []
safeMFC12 = []
safeMFC13 = []
safeMFC14 = []
safeMFC15 = []
safeMFC16 = []
safeMFC17 = []
safeMFC18 = []
safeTimeCard1 = []

def getExpBMFCs():
    lock.acquire()
    expAMFCs = [C1MFC1, C1MFC2, C1MFC3, C1MFC4, C1MFC5, C1MFC6, C1MFC7, C1MFC8, C1MFC9]
    lock.release()
    return expAMFCs

def getExpCMFCs():
    lock.acquire()
    expBMFCs = [C1MFC10, C1MFC11, C1MFC12, C1MFC13, C1MFC14, C1MFC15, C1MFC16, C1MFC17, C1MFC18]
    lock.release()
    return expBMFCs

#def getExpAMFCsVectors():
    #lock.acquire()
    #expAMFCs = [safeMFC1, safeMFC2, safeMFC3, safeMFC4, safeMFC5, safeMFC6, safeMFC7, safeMFC8, safeMFC9]
    #lock.release()
    #return expAMFCs

class Agilent():
    #This is the function that you call in multipleExperiments, line 33
    def __init__(self, queueB = None, queueC = None):
        #threading.Thread.__init__(self)
        self.queueB = queueB
        self.queueC = queueC
        self.name = "agilent" #Name of the experimen (used in the log)
        self.startTime = datetime.datetime.now()
        self.folder = "log/"
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.logFile = self.folder + self.name + '_log-{}.csv'.format(self.startTime.strftime("%Y-%m-%d %H.%M.%S"))

        
        #Create the log of the experiment
        with open(self.logFile, 'wb') as f:
            self.writer = csv.writer(f, delimiter=',')
            self.writer.writerow([
                'Day',
                'Time',
                'Function',
            ])
        
    
    def setup(self):
        #register the sampling task into the schedule
        #This function (sampleMFCs) will be called every 3 minutes
        #schedule.every().day.at("13:30").do(self.feedMFCs)

        schedule.every(3).minutes.do(self.sampleMFCs)
        #schedule.every(5).seconds.do(self.sampleMFCs)

        
    def update(self):
        global lock
        global safeMarkers
      
        #while True:
        schedule.run_pending()
        #    time.sleep(1)
            

################################################################################
#         Function that feeds the MFCs, it is called every day                 #
################################################################################
    def sampleMFCs(self):
        functionName = "sampling MFCs"
        print functionName
        self.agilentScan()
        #self.fakeAgilentScan()
        self.log(functionName)

        
        

    def getMFCsExpB(self):
        #TODO
        print " "
        
    def getMFCsExpC(self):
        #TODO
        print " "


    def log(self, functionName):
        currentTime = datetime.datetime.now()
        with open(self.logFile, 'ab') as f:
            self.writer = csv.writer(f, delimiter=',')
            self.writer.writerow([
                currentTime.strftime("%Y.%m.%d"),
                currentTime.strftime("%H.%M.%S"),
                functionName,
            ])
            
    def fakeAgilentScan(self):
            
            timeNow = datetime.datetime.now()
            #today2 = time.strftime("%d.%m.%Y %H:%M:%S", timeNow) #get current time
            
            lock.acquire()
            C1MFC1 = 1.0#random.random()
            C1MFC2 = 2.0#random.random()
            C1MFC3 = 3.0#random.random()
            C1MFC4 = random.random()
            C1MFC5 = random.random()
            C1MFC6 = random.random()
            C1MFC7 = random.random()
            C1MFC8 = random.random()
            C1MFC9 = random.random()
            C1MFC10 = random.random()
            C1MFC11 = random.random()
            C1MFC12 = random.random()
            C1MFC13 = random.random()
            C1MFC14 = random.random()
            C1MFC15 = random.random()
            C1MFC16 = random.random()
            C1MFC17 = random.random()
            C1MFC18 = random.random()
            C1MFC19 = random.random()
            C1MFC20 = random.random()
            lock.release()
            
            vector = [timeNow, C1MFC1, C1MFC2, C1MFC3, C1MFC4, C1MFC5, C1MFC6, C1MFC7, C1MFC8, C1MFC9]
            if self.queueB is not None:
                self.queueB.put(vector)
            vector = [timeNow, C1MFC10, C1MFC11, C1MFC12, C1MFC13, C1MFC14, C1MFC15, C1MFC16, C1MFC17, C1MFC18]
            if self.queueC is not None:
                self.queueC.put(vector)
            return [C1MFC1, C1MFC2, C1MFC3, C1MFC4, C1MFC5, C1MFC6, C1MFC7, C1MFC8, C1MFC9, C1MFC10, C1MFC11, C1MFC12,
                    C1MFC13, C1MFC14, C1MFC15, C1MFC16, C1MFC17, C1MFC18, C1MFC19, C1MFC20]

    def agilentScan(self):

        try:
            print "Agilent DA OPP"
            Card1voltage='0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,\n'

            
            rm = visa.ResourceManager()
            inst = 'USB0::2391::8199::MY49012441::0::INSTR'
            agilent = rm.open_resource(inst)
            print(agilent.query('*IDN?'))
            agilent.write("*RST")
            agilent.write("*CLS")
            agilent.write('CONFigure:VOLTage:DC 1,(@101:120)')
            agilent.write('SENSe:VOLTage:DC:NPLC 1,(@101:120)')
            agilent.write("ROUTe:CHANnel:DELay 0,(@101:120) ")
            print(agilent.query('ROUTe:SCAN?'))
            ##agilent.write('TRIGger:COUNt 1')
            ##agilent.write('TRIGger:SOURce TIMer')
            ##agilent.write('TRIGger:TIMer 10')
            time.sleep(1)
            ##print "scan"
            agilent.write('INITiate')
            time.sleep(5)
            agilent.write('FETC?')

            Card1voltage = agilent.read() #saves all the values as an array
            print Card1voltage
            #print(agilent.read())
            agilent.write("*RST")
            agilent.write("*CLS")
            agilent.close()
            rm.close()

            today1 = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
            C1MFC1, C1MFC2, C1MFC3, C1MFC4, C1MFC5, C1MFC6, C1MFC7, C1MFC8, C1MFC9, C1MFC10, C1MFC11, C1MFC12, C1MFC13, C1MFC14, C1MFC15, C1MFC16, C1MFC17, C1MFC18, C1MFC19, C1MFC20 = Card1voltage.split(',')
            #saves the measured values in variables NUMBER OF VARIABLES NEED TO BE THE SAME THAN THE MEASURED CHANNELS OR ELSE YOU WILL GET AN ERROR MESSAGE!
            C1MFC20 = C1MFC20.rstrip('\n') #last value still contains the new line command which needs to be deleted
           
            print "write logfile"
            Card1txt = ''
            Card1txt = today1 + '\t' + str(C1MFC1) + '\t' + str(C1MFC2) + '\t' + str(C1MFC3) + '\t' + str(C1MFC4) + '\t' + str(C1MFC5) + '\t' + str(C1MFC6) + '\t' + str(C1MFC7) + '\t' + str(C1MFC8) + '\t' + str(C1MFC9) + '\t' + str(C1MFC10) + '\t' + str(C1MFC11) + '\t' + str(C1MFC12) + '\t' + str(C1MFC13) + '\t' + str(C1MFC14) + '\t' + str(C1MFC15) + '\t' + str(C1MFC16) + '\t' + str(C1MFC17) + '\t' + str(C1MFC18) + '\t' + str(C1MFC19) + '\t' + str(C1MFC20) + '\n'
            logfile1 = open('Voltage_Card1.txt', 'a') #appends the logfile
            logfile1.write(Card1txt)
            logfile1.close()

            Card1txt = ''
            Card1txt = today1 + '\t' + str(float(C1MFC1)/1000) + '\t'+ str(float(C1MFC2)/1000) + '\t'+ str(float(C1MFC3)/1000) + '\t'+ str(float(C1MFC4)/1000) + '\t'  + str(float(C1MFC5)/1000) + '\t'+ str(float(C1MFC6)/1000) + '\t'+ str(float(C1MFC7)/1000) + '\t'+ str(float(C1MFC8)/1000) + '\t'+ str(float(C1MFC9)/1000) + '\t'+ str(float(C1MFC10)/1000) + '\t'+ str(float(C1MFC11)/1000) + '\t'+ str(float(C1MFC12)/1000) + '\t'+ str(float(C1MFC13)/1000) + '\t'+ str(float(C1MFC14)/1000) + '\t'+ str(float(C1MFC15)/1000) + '\t'+ str(float(C1MFC16)/1000) + '\t'+ str(float(C1MFC17)/1000) + '\t'+ str(float(C1MFC18)/1000) + '\t'+ str(float(C1MFC19)/1000) + '\t' + '\t'+'\n'
            logfile1 = open('CurrentCard1.txt', 'a') #appends the logfile
            logfile1.write(Card1txt)
            logfile1.close()

            timeNow = datetime.datetime.now()
            
            vector = [timeNow, C1MFC1, C1MFC2, C1MFC3, C1MFC4, C1MFC5, C1MFC6, C1MFC7, C1MFC8, C1MFC9]
            if self.queueB is not None:
                self.queueB.put(vector)
            vector = [timeNow, C1MFC10, C1MFC11, C1MFC12, C1MFC13, C1MFC14, C1MFC15, C1MFC16, C1MFC17, C1MFC18]
            if self.queueC is not None:
                self.queueC.put(vector)
            return [C1MFC1, C1MFC2, C1MFC3, C1MFC4, C1MFC5, C1MFC6, C1MFC7, C1MFC8, C1MFC9, C1MFC10, C1MFC11, C1MFC12, C1MFC13, C1MFC14, C1MFC15, C1MFC16, C1MFC17, C1MFC18, C1MFC19, C1MFC20]
        except:

            print "Agilent not connected?"
            return None
            #quit_prog()


