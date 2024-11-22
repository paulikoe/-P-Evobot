import cv2, sys
import numpy as np
from matplotlib import pyplot as plt
from time import sleep
sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
import math
import threading
import VisionTools as vt
import threading,time
from evocam import EvoCam
from datalogger import DataLogger
from syringe import Syringe
from head import Head
import json
import datetime
import time
from droplet import Droplet

Trackbars=[['syringeD',0, -1 * SYRINGES['SYRINGE1']['SYRINGE_LIMIT']],['plungerVol',0, 2* SYRINGES['SYRINGE1']['PLUNGER_LIMIT']]]
windowName='result'
candidateMx,candidateMy,candidatePx,candidatePy=0,0,0,0
injection=[{},{}]
lclickNr=0

#--------------------------
#         Global variable
#--------------------------
global head,syringe



def lCAction(x,y,sD,plungerVol):
    global head,syringe

    head.move( x, y)
    syringe.syringeMove( -sD )
    if plungerVol >=0:
        syringe.plungerPushVol( plungerVol)
    elif plungerVol<0:
        syringe.plungerPullVol(- plungerVol)
    syringe.syringeMove( 0 )





def chemistControl():

    global sD,syringeD,plungerVol,injection
    global candidatePx,candidatePy
    global dropletPx,dropletPy,dropletMx,dropletMy,dropletPxIni,dropletPyIni,dropletMxIni,dropletMyIni 
    global dropletContour,dropletAreaP,dropletAreaM
    global M,iM
    global evocam
    M=None
    img = None
    mask = None
    global hsv
    global evobot
    ix=50
    iy=50
    hsv_pixel=[[[160,255,255]]]
    cnt=0
    recording=False
    timeList=[]

    # mouse callback function


    cv2.namedWindow(windowName)
    vt.createTrackbars(windowName,Trackbars)

    cap = cv2.VideoCapture(CAMERA_ID)
    _,img = cap.read()
    x, y, z = img.shape
    mask2 = np.zeros((x, y, 3), np.uint8)
    mask2.fill(255)
    cv2.setMouseCallback('result',center_coordinate)


    # Starting with 100's to prevent error while masking
    h,s,v = 100,100,100
    #M=np.load('../../calibration/' + str(SYRINGES['SYRINGE1']['ID']) +'.npy')
    M=syringe.affineMat
    iM=cv2.invertAffineTransform(M)



    while(1):

        _, newimg = cap.read()
        rows,cols,ch = newimg.shape


        (_,_,dropletPx,dropletPy,dropletAreaP,_,dropletMx,dropletMy,dropletAreaM,_,)=redDroplet.getData()
        
        dropletContour=redDroplet.getContour()


    #trackbars
        dic=vt.getTrackbars(windowName,Trackbars)
        syringeD=dic['syringeD']
        plungerV=dic['plungerVol']
        plungerVol=plungerV- SYRINGES['SYRINGE1']['PLUNGER_LIMIT']
        string1="syringeD:" + str(syringeD)
        if plungerVol>=0:

            string2="plungerPush:" + str(plungerVol)
        elif plungerVol<0:
            string2="plungerPull:" + str(-plungerVol)

        if recording is True:
            string3='Recording'
        elif recording is False:
            string3='Not recording'

        vt.setText(newimg,(20,20),string1)
        vt.setText(newimg,(20,40),string2)
        vt.setText(newimg,(20,60),string3)

        #left click
        t1=time.time()


        #timeList.append(t1)
        #if cnt>2:

            #   frameratePS=1/(timeList[cnt]-timeList[cnt-1])
            #  print frameratePS

        if lclickNr>0:              
            for lclickN in xrange(1,lclickNr+1):
                if injection[lclickN]['t0'] is not None:

                    injection[lclickN]['timer']=round( t1- injection[lclickN]['t0'],1)
                    injection[lclickN]['radius']=int(10 * math.sqrt(injection[lclickN]['timer']))
                    #show on window
                    vt.setText(newimg,(injection[lclickN]['saltx']+10,injection[lclickN]['salty']+10),str(injection[lclickN]['timer']))
                    cv2.circle(newimg,(injection[lclickN]['saltx'],injection[lclickN]['salty']),injection[lclickN]['radius'], (255,0,0),4)


        #right click
        if candidatePx<>0 and candidatePy<>0:
            cv2.circle(newimg,(candidatePx,candidatePy), 2, (0,0,255),4)
            #cv2.line(newimg, (candidatePx, candidatePy), (20, 20), (0,0,0))
            cv2.line(newimg, (candidatePx, candidatePy), (dropletPxIni, dropletPyIni), (0,0,0))
            #distance=vt.Distance((candidateMx,candidatePy),(20,20))
            distance=vt.Distance((candidateMx,candidateMy),(dropletMxIni,dropletMyIni))
            vt.setText(newimg,(candidatePx+10,candidatePy+30),str(distance))


        #droplet
        cv2.drawContours(newimg,dropletContour, -1, (0,255,0), 3)
        cv2.circle(newimg,(dropletPx,dropletPy), 2, (0,0,255),4)
        cv2.putText(newimg,"Area:" + str(dropletAreaP)+ ";" + str(int(dropletAreaM)), (dropletPx+20,dropletPy+80), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
        cv2.putText(newimg,"Center:" + str(dropletPx) + ',' +str(dropletPy)+ ";" + str(int(dropletMx)) + ',' +str(int(dropletMy)), (dropletPx+20,dropletPy+100), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)        



        if recording is True:
            videowriter.write(newimg)

        cv2.imshow(windowName,newimg)
        cnt+=1

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
        if(k==ord('s')):
            print "saving"
            dropletInfo=evocam.getDroplet()
            gooz=dropletInfo[0:][0:5] + dropletInfo[0:][7:]
            dropletNp=np.asarray(dropletInfo, dtype=object)
            #f = open('output.txt', 'w')
            #f.writelines( dropletInfo( "%s\n" % item for item in dropletInfo ) )
            #f.close()
            #open('filenamess', 'w').write('\n'.join('%s' % x for x in dropletInfo))
            #for t in dropletInfo:
                #  open('filenamess', 'w').write(' '.join(str(s) for s in t) + '\n')         
            np.save('dropletInfo', dropletNp)

        if(k==ord('r')):
            print "recording"
            recording=True
            recordFileName=vt.removeColon(str(datetime.datetime.now()))
            print recordFileName
            videowriter=vt.saveVideo(recordFileName,(rows,cols))

        if(k==ord('p')):
            print "stoping recording"
            recording=False
            videowriter.release()


    cap.release()
    cv2.destroyAllWindows()



def center_coordinate(event,x,y,flags,param):
    global ix,iy, hsv_pixel,saltx,salty,M,iM,sD,syringeD,plungerVol,candidatePx,candidatePy,t0,injection,lclickNr
    global candidateMx,candidateMy
    global dropletPx,dropletPy,dropletMx,dropletMy,dropletPxIni,dropletPyIni,dropletMxIni,dropletMyIni


    if event == cv2.EVENT_LBUTTONDOWN:
        lclickNr+=1


        injection[lclickNr]['saltx'],injection[lclickNr]['salty']=x,y
        #print "droplx,droply:" + str(droplx) + "," + str(droply)
        impixel=np.float32([injection[lclickNr]['saltx'],injection[lclickNr]['salty'],1])
        RobCor=np.dot(M, impixel)
        if plungerVol>0:

            injection[lclickNr]['t0']=time.time()
        elif plungerVol<=0:
            injection[lclickNr]['t0']=None
        for sth in xrange(1,lclickNr+1):
            print injection[sth]['t0']
        injection.append({})


        threading.Thread(target=lCAction,args=(RobCor[0], RobCor[1],syringeD,plungerVol)).start()





    if event == cv2.EVENT_RBUTTONUP:
        candidatePx,candidatePy=x,y
        impixel=np.float32([candidatePx,candidatePy,1])
        candidate=np.dot(M, impixel)
        candidateMx,candidateMy=candidate[0],candidate[1]
        dropletPxIni,dropletPyIni=dropletPx,dropletPy
        dropletMxIni,dropletMyIni=dropletMx,dropletMy



def initialize():
    global head,syringe,evobot

    usrMsgLogger = DataLogger()
    evobot = EvoBot( PORT_NO, usrMsgLogger)
    head = Head( evobot )
    syringe =  Syringe( evobot, SYRINGES['SYRINGE1'])
    evobot.home()
    #syringe.plungerMoveToDefaultPos()








def run():


    global dropletPx,dropletPy,dropletMx,dropletMy,dropletContour,dropletAreaP,dropletAreaM,dropletInfo,evocam, redDroplet
    initialize()


    evocam=EvoCam(evobot)
    redDroplet=Droplet(color='default red', lowerhsv=None,upperhsv=None,minSizemm=None,maxSizemm=None,
                       minSizePix=100,maxSizePix=7000,dataLoggerName='multitrackingred',contourColor='red')


    evocam.trackDroplet(redDroplet,syringe)
    evocam.record( 'chemistMode' , extension='.mkv')    


    chemistControl()





#main

run()