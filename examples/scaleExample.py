#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "anfv"
__date__ = "$12-Aug-2016 14:26:32$"


import time
import sys
sys.path.append('../api')
from scale_kern_pcb import Scale
from configuration import *
import numpy as np

measurements=[]
scale = Scale(SCALE_PORT_NO)
#Tare scale
scale.tare()

print "Ready to start the measurements, place a object on the scale and press a key."
sys.stdin.readline()

for x in range(0,5):
    
    m = scale.stableWeigh()
    measurements.append(m)
    print "Weight is " + str(m) 
    
    #Tare scale
    scale.tare()
    
    
    print "Place a object on the scale and press a key."
    sys.stdin.readline()
    
scale.quit()
print measurements
print np.average(measurements)
print np.std(measurements)
print "End"


