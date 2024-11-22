import cv2, sys
import numpy as np
from time import sleep
sys.path.append('../api')
from evobot import EvoBot
import threading
import VisionTools as vt
from datalogger import DataLogger
from syringe import Syringe
from head import Head
import time

#syringe needle is .96 mm

printString='R E A L '


def initializeEvobot():
    global head,syringe,evobot
    usrMsgLogger = DataLogger()
    evobot = EvoBot("/dev/tty.usbmodemfd121", usrMsgLogger)
    head = Head( evobot )
    syringe =  Syringe( evobot, 13)
    syringe.plungerSetConversion( 1 )
    #evobot.home()   
    #syringe.plungerPushVol(1)
    
    


def makeBubble((printPointX,printPointY),(x,y)):
    head.move( printPointX-x, printPointY+y )
    time.sleep(1)
    syringe.syringeMove( -66 )
    time.sleep(1)
    syringe.plungerPushVol(.05)
    time.sleep(1)
    #head.move( printPointX+x+5, printPointY+y )
    syringe.syringeMove( -60 )    
    time.sleep(1)
    

def count_letters(word):
    BAD_LETTERS = " "
    return len([letter for letter in word if letter not in BAD_LETTERS])


def droplet3dPrinter(printString,(printPointX,printPointY),(heightmm,widthmm)=(40,160), minDistancemm=3):
    
    i,j=0,0
    points=[]
    ratio=heightmm/40
    #ratio=2
    blank_img=np.zeros((40 * ratio, 20 * ratio * count_letters(printString),3),np.uint8)
    cv2.putText(blank_img,printString, (20,20*ratio), cv2.FONT_HERSHEY_SIMPLEX, ratio* .5, (255,255,255),1)
    gray=cv2.cvtColor(blank_img, cv2.COLOR_BGR2GRAY)
    h,w=gray.shape
    
    for row in gray:
        for colon in row:
            if j==w:
                j=0            
            if colon==255:
                points.append([i,j])
    
            j+=1
        i+=1
    
    sampled=[]
    wanted=True
    for point1 in points:
        for point2 in sampled:
            if vt.Distance(point1,point2) < minDistancemm:
                wanted=False
        if wanted is True:
            sampled.append(point1)
        wanted=True
    
    
    
    sampled_img=np.zeros((h,w),np.uint8)
    printed_img=np.zeros((h,w),np.uint8)
    for po in sampled:
        sampled_img[po[0],po[1]]=255 
    cv2.imshow('sampled Text', sampled_img)
    
    for po2 in sampled:
        makeBubble((printPointX,printPointY),(po2[0],po2[1]))  
        printed_img[po2[0],po2[1]]=255
        cv2.imshow('printed Bubbles', printed_img)
        cv2.waitKey(1)

    
initializeEvobot()
droplet3dPrinter(printString,(130,0),(80,320),5)
    
    