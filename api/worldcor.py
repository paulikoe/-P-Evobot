import cv2
import numpy as np


class WorldCor:
    def __init__(self, syringe, mode='default', method='all'):
        """
        This method initialize the WorldCor object. The parameters
        are the
        """
        self.syringe = syringe
        self.method = method
        self.mode = mode
        self.h1 = 28
        self.h2 = 56
        self.d1 = 123
        self.d2 = 53.3

    def worldCorFor(self, src, syringe, pixels=False):
        if self.mode == 'default':
            world = self.offset(self.syringe)
            offset = self.offset(syringe)
            worldmm = (src[0] + round(offset[0] - world[0], 1), src[1] + round(offset[1] - world[1], 1))
        elif self.mode == 'camera':
            self.worldMat = np.load(str(self.syringe.syringeID) + '.npy')
            self.worldMatInv = cv2.invertAffineTransform(self.worldMat)
            self.mat = np.load(str(syringe.syringeID) + '.npy')
            self.matInv = cv2.invertAffineTransform(self.mat)
            pix = self.mmTopix(src)
            worldmm = self.pixTomm(self.mat, pix)
        return worldmm

    def mmTopix(self, point):
        self.worldMat = np.load('../../calibration/affinemat/' + str(self.syringe.syringeID) + '.npy')
        self.worldMatInv = cv2.invertAffineTransform(self.worldMat)        
        pointHom = [point[0], point[1], 1]
        pix = np.dot(self.worldMatInv, pointHom)
        return pix

    def pixTomm(self, mat, point):
        pointHom = [point[0], point[1], 1]
        mm = np.dot(mat, pointHom)
        return mm

    def offset(self, syringe):
        if isinstance(syringe, int):
            syringeID = syringe
        else:
            syringeID = syringe.syringeID
        #this is a quick method for calibration based on the dimensions of the robot, however may not be precise
        #due to different syringe sizes!!
        if self.method =='quick':
            if syringeID == 0:
                z = 0
                x = 2 * (self.h2)
            elif syringeID == 1:
                x, z = 0, 0
            # same z
            elif syringeID == 2:
                z = self.d1
                x = 2 * (self.h2)
            elif syringeID == 3:
                z = self.d1
                x = self.h1 + self.h2
            elif syringeID == 4:
                z = self.d1
                x = self.h2
            elif syringeID == 5:
                z = self.d1
                x = self.h1
            elif syringeID == 6:
                z = self.d1
                x = 0
    
            # same z
            elif syringeID == 7:
                z = self.d1 + self.d2
                x = 2 * (self.h2)
            elif syringeID == 8:
                z = self.d1 + self.d2
                x = self.h1 + self.h2
            elif syringeID == 9:
                z = self.d1 + self.d2
                x = self.h2
            elif syringeID == 10:
                z = self.d1 + self.d2
                x = self.h1
            elif syringeID == 11:
                z = self.d1 + self.d2
                x = 0
    
            # same z
            elif syringeID == 12:
                z = 2 * (self.d1) + self.d2
                x = 2 * (self.h2)
            elif syringeID == 13:
                z = 2 * (self.d1) + self.d2
                x = self.h1 + self.h2
            elif syringeID == 14:
                z = 2 * (self.d1) + self.d2
                x = self.h2
            elif syringeID == 15:
                z = 2 * (self.d1) + self.d2
                x = self.h1
            elif syringeID == 16:
                z = 2 * (self.d1) + self.d2
                x = 0
                
        #this mehtod is precise calibration but takes more time
        #to calibrate using this method all syringes need to go to the same point, and calculate the offset for those points
        if self.method =='all':
            if syringeID == 0:
                z = 0
                x = 2 * (self.h2)
            elif syringeID == 1:
                x, z = 0, 0
            # same z
            elif syringeID == 2:
                z = self.d1
                x = 2 * (self.h2)
            elif syringeID == 3:
                z = self.d1
                x = self.h1 + self.h2
            elif syringeID == 4:
                z = 118
                x = 56
            elif syringeID == 5:
                z = self.d1
                x = self.h1
            elif syringeID == 6:
                z = self.d1
                x = 0
        
            # same z
            elif syringeID == 7:
                z = self.d1 + self.d2
                x = 2 * (self.h2)
            elif syringeID == 8:
                z = self.d1 + self.d2
                x = self.h1 + self.h2
            elif syringeID == 9:
                z = self.d1 + self.d2
                x = self.h2
            elif syringeID == 10:
                z = self.d1 + self.d2
                x = self.h1
            elif syringeID == 11:
                z = 147
                x = 2
        
            # same z
            elif syringeID == 12:
                z = 2 * (self.d1) + self.d2
                x = 2 * (self.h2)
            elif syringeID == 13:
                z = 2 * (self.d1) + self.d2
                x = self.h1 + self.h2
            elif syringeID == 14:
                z = 2 * (self.d1) + self.d2
                x = self.h2
            elif syringeID == 15:
                z = 264.6
                x = 26
            elif syringeID == 16:
                z = 2 * (self.d1) + self.d2
                x = 0        
        return x, z

    def inverseWorldCorFor(self, src, syringe, pixels=False):
        if self.mode == 'default':
            world = self.offset(self.syringe)
            offset = self.offset(syringe)
            worldmm = (src[0] - round(offset[0] - world[0], 1), src[1] - round(offset[1] - world[1], 1))
        return worldmm
