import cv2
import numpy as np
import sys
sys.path.append('../api')
sys.path.append('../settings')
from configuration import *


img = None
mask = None
global hsv
ix=50
iy=50
droplx=0
droply=0
hsv_pixel=[[[160,255,255]]]
M1= np.load('affinemat/'+ str(SYRINGES['SYRINGE1']['ID']) +'.npy')
A=M1[0:2,0:2]
detA= abs(np.linalg.det(A))
areaBuf=[]
bufLen=100
cyBuf,cxBuf=[],[]
cntBufLen=1


# mouse callback function
def center_coordinate(event,x,y,flags,param):
    global ix,iy, hsv_pixel,droplx,droply
    
    if event == cv2.EVENT_RBUTTONUP:   
        ix=x
        iy = y    
    elif event == cv2.EVENT_LBUTTONDOWN:
        droplx=x
        droply=y
        GBRpixel= img [x,y]
        hsvpix = np.uint8([[GBRpixel]])
        hsv_pixel = cv2.cvtColor(hsvpix,cv2.COLOR_BGR2HSV)
        
# Create a black image, a window and bind the function to window
cv2.namedWindow('result')
cap = cv2.VideoCapture(CAMERA_ID)
_,img = cap.read()
x, y, z = img.shape
mask2 = np.zeros((x, y, 3), np.uint8)
mask2.fill(255)
cv2.setMouseCallback('result',center_coordinate)

def nothing(x):
    
    pass

# Starting with 100's to prevent error while masking
h,s,v = 100,100,100

# Creating track bar
selectColor = '0 : Blue \n1 : Red \n2 : Manual'
cv2.createTrackbar('selectColor', 'result',0,3,nothing)
cv2.createTrackbar('hUpper', 'result',179,179,nothing)
cv2.createTrackbar('hLower', 'result',0,179,nothing)
cv2.createTrackbar('sLower', 'result',0,255,nothing)
cv2.createTrackbar('vUpper', 'result',255,255,nothing)
cv2.createTrackbar('sUpper', 'result',255,255,nothing)
cv2.createTrackbar('vLower', 'result',0,255,nothing)
cv2.createTrackbar('R', 'result',300,1000,nothing)


while(1):

    _, frame = cap.read()
    frame=cv2.blur(frame,(3,3))
    
    mask2.fill(0)
    
    R = cv2.getTrackbarPos('R','result')
    cv2.circle(mask2, (ix, iy), R, (255, 255, 255), -1)
    frame = cv2.bitwise_and(frame, mask2)
    #converting to HSV
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    # get info from track bar and appy to result
    selection = cv2.getTrackbarPos('selectColor','result')
    hUpper = cv2.getTrackbarPos('hUpper','result')
    hLower = cv2.getTrackbarPos('hLower','result')
    sLower = cv2.getTrackbarPos('sLower','result')
    sUpper = cv2.getTrackbarPos('sUpper','result')
    vLower = cv2.getTrackbarPos('vLower','result')
    vUpper = cv2.getTrackbarPos('vUpper','result')
    
    if selection==0:
        lower_blue = np.array([hLower,sLower,vLower])
        upper_blue = np.array([hUpper,sUpper,vUpper])
        numberToColor="Manual Mode"
    elif selection==1:
        lower_blue = np.array([140,40,40])
        upper_blue = np.array([180,255,255])
        numberToColor="red"
    elif selection==2:
        lower_blue = np.array([60,50,50])
        upper_blue = np.array([160,255,255])
        numberToColor="blue"
    else:        
        # Normal masking algorithm
        lower_blue = np.array([hLower,sLower,vLower])
        upper_blue = np.array([hUpper,sUpper,vUpper])
        numberToColor="green"

    mask = cv2.inRange(hsv,lower_blue, upper_blue)
    result = cv2.bitwise_and(frame,frame,mask = mask)
    
    # noise removal
    #kernel = np.ones((4,4),np.uint8)
    #opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
    #closing = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel, iterations = 2)
    #closeOpen=cv2.morphologyEx(closing,cv2.MORPH_OPEN,kernel, iterations = 2)

    #mask=closeOpen   

    st = cv2.getStructuringElement(cv2.MORPH_CROSS,(15,15))        
    kernel = np.ones((9,9),np.uint8)
    thresh_close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations = 1)
    thresh_open= cv2.morphologyEx(thresh_close, cv2.MORPH_OPEN, kernel, iterations = 1)    
    mask=thresh_open    
    #cv2.imshow('close', thresh_close)
    #cv2.imshow('open', thresh_open)
    
    _,contours,hierarchy = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    
    # finding contour
    max_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
       
        if area > 300 and area<30000:
            #max_area = area
            areaBuf.append(area)
            if len(areaBuf) > bufLen:
                del areaBuf[0]
            max_area = np.mean(areaBuf)
            best_cnt=cnt
            # finding centroids of best_cnt and draw a circle there
            M = cv2.moments(best_cnt)
            cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cxBuf.append(cx)
            if len(cxBuf) > cntBufLen:
                del cxBuf[0]
            cx = np.mean(cxBuf)  
            cyBuf.append(cy)
            if len(cyBuf) > cntBufLen:
                del cyBuf[0]
            cy = np.mean(cyBuf)             
            
            rows,cols,ch = best_cnt.shape           
            cv2.drawContours(result, best_cnt, -1, (0,255,0), 3)
            cv2.putText(result,"Area(pixel):" + str(round(max_area,2)), (int(cx)+20,int(cy)+60), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            cv2.putText(result,"Area(mm2):" + str(round(max_area* detA,2)), (int(cx)+20,int(cy)+80), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            cv2.putText(result,"Droplet Center(pixel):" + str(int(cx)) + ',' +str(int(cy)), (int(cx)+20,int(cy)+100), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            
            centerPixel=np.float32([cx,cy,1])
            CenterCor=np.dot(M1, centerPixel)
    
            cv2.putText(result,"Droplet Center(mm):" + str(round(CenterCor[0],2)) + ',' +str(round(CenterCor[1],2)), (int(cx)+20,int(cy)+120), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            cv2.circle(result,(int(cx),int(cy)),5,255,-1)

    
    hrange= "Hue range:" + str(hLower) + "_" + str(hUpper)
    cv2.putText(result,hrange, (20,20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    srange= "Saturation range:" + str(sLower) + "_" + str(sUpper)
    cv2.putText(result,srange, (20,40), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    vrange= "Value range:" + str(vLower) + "_" + str(vUpper)
    cv2.putText(result,vrange, (20,60), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    Radius= "Radius:" + str(R)
    cv2.putText(result,Radius, (20,80), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    ColorToDetect= "Color to Detect:" + str(numberToColor)
    cv2.putText(result,ColorToDetect, (20,100), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    cv2.putText(result,str(hsv_pixel), (droplx,droply), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    cv2.putText(result,"coordinate(pixel):" + str(droplx)+","+ str(droply), (droplx,droply+20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    impixel=np.float32([droplx,droply,1])
    RobCor=np.dot(M1, impixel)
    
    cv2.putText(result,"coordinate(mm):" + str(RobCor[0])+","+ str(RobCor[1]), (droplx,droply+40), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    

    cv2.imshow('result',result)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()