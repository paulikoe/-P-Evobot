import cv2
import numpy as np
import pylab
from pylab import *
import matplotlib as mpl 
import math
from scipy import linalg



def calibrateCamera(camNum =0,nPoints=5,patternSize=(9,6),saveImage=False):
    ''' CalibrateCamera captures images from camera (camNum)
        The user should press spacebar when the calibration pattern
        is in view.
        When saveImage is a boolean it indicates whether the images used for calibration should be saved
        When it is True the image will be saved into a default filename. When saveImage is a string the images
        will be saved using the string as the filename.
    '''
    print('click on the image window and then press the space bar to take samples')
    cv2.namedWindow("camera",1)
    pattern_size=patternSize
    n=nPoints #number of images before calibration
    #temp=n
    calibrated=False
    square_size=1
    pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
    pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size

    camera_matrix = np.zeros((3, 3))
    dist_coefs = np.zeros(4) 
    rvecs=np.zeros((3, 3))
    tvecs=np.zeros((3, 3))

    obj_points = []
    img_points = []

    capture = cv2.VideoCapture(camNum)
    imgCnt = 0
    running = True
    while running:

        ret, imgOrig =capture.read()
        img= imgOrig.copy()
        h, w = img.shape[:2]
        imgGray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if (calibrated==False):
            found,corners=cv2.findChessboardCorners(imgGray, pattern_size  )
        ch = cv2.waitKey(1)

        if(ch==27): #ESC
            running = False
            found = False
            d = False
            return (calibrated,None,None,None)

        if (found!=0)&(n>0):
            cv2.drawChessboardCorners(img, pattern_size, corners,found)
            if ((ch == 13) or (ch==32)): #enter or space key :
                term = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1 )
                cv2.cornerSubPix(imgGray, corners, (5, 5), (-1, -1), term)

                img_points.append(corners.reshape(-1, 2))
                obj_points.append(pattern_points)
                n=n-1 
                imgCnt=imgCnt+1;    
                print('sample %s taken')%(imgCnt)
                if(saveImage!=False):
                    if(saveImage==True):
                        fileName = 'CalibrationImage'+str(imgCnt)+".jpg"
                    else:
                        fileName =saveImage+str(imgCnt)+".jpg"
                    print("saving Image " + fileName)
                    cv2.imwrite(fileName,imgOrig)
                if n==0:
    #                print( img_points)
    #                print(obj_points)     
                    rms, camera_matrix, dist_coefs, rvecs, tvecs  = cv2.calibrateCamera(obj_points, img_points, (w, h),camera_matrix,dist_coefs,flags = 0)
    #               print "RMS:", rms
                    print ("camera matrix:\n", camera_matrix)
                    print ("distortion coefficients: ", dist_coefs)
                    np.save('camera_matrix', camera_matrix)
                    np.save('distortionCoefficient', dist_coefs)                    
                    calibrated=True

                    return (calibrated, camera_matrix, dist_coefs,rms)

        elif(found==0)&(n>0):
            print("chessboard not found")


        #if (calibrated):
        #    img=cv2.undistort(img, camera_matrix, dist_coefs )
        #    found,corners=cv2.findChessboardCorners(imgGray, pattern_size  )
        #    if (found!=0):
        #        cv2.drawChessboardCorners(img, pattern_size, corners,found)

        cv2.imshow("camera", img)


class Camera:
    """ Class for representing pin-hole cameras. """

    def __init__(self,P):
        """ Initialize P = K[R|t] camera model. """
        self.P = P
        self.K = None # calibration matrix
        self.R = None # rotation
        self.t = None # translation
        self.c = None # camera center


    def project(self,X):
        """	Project points in X (4*n array) and normalize coordinates. """

        x = dot(self.P,X)
        for i in range(3):
            x[i] /= x[2]
        return x


    def factor(self):
        """	Factorize the camera matrix into K,R,t as P = K[R|t]. """

        # factor first 3*3 part
        K,R = linalg.rq(self.P[:,:3])

        # make diagonal of K positive
        T = diag(sign(diag(K)))

        self.K = dot(K,T)
        self.R = dot(T,R) # T is its own inverse
        self.t = dot(linalg.inv(self.K),self.P[:,3])

        return self.K, self.R, self.t


    def center(self):
        """	Compute and return the camera center. """

        if self.c is not None:
            return self.c
        else:
            # compute c by factoring
            self.factor()
            self.c = -dot(self.R.T,self.t)
            return self.c


    def calibrate_from_points(x1,x2):

        return self.K


    def simple_calibrate(a,b):

        return self.K


# helper functions

def rotation_matrix(a):
    """	Creates a 3D rotation matrix for rotation
         around the axis of the vector a. """
    R = eye(4)
    R[:3,:3] = linalg.expm([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return R


def rq(A):
    from scipy.linalg import qr

    Q,R = qr(flipud(A).T)
    R = flipud(R.T)
    Q = Q.T

    return R[:,::-1],Q[::-1,:]
