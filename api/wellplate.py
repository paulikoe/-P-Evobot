import time
import threading
import datetime
import sys
from syringe import Syringe
from head import Head
import re
from petridish import PetriDish
from worldcor import WorldCor


class WellPlate:
    def __init__(self, _evobot, _head, plateRows=8, plateCols=12, wellDiameter=9, tLeftCorner=None, dRightCorner=None,
                 worldCor=None):

        self.plateRows = plateRows
        self.plateCols = plateCols
        self.wellDiameter = wellDiameter
        self.tLeftCorner = tLeftCorner
        self.dRighCorner = dRightCorner
        self.evobot = _evobot
        self.head = _head
        self.dateLogger = None
        self.event = threading.Event()
        self.worldCor = worldCor

    def fillAll(self, syringe, petridish, dispenseVol, dispensePos, upPos):
        """
        This method fills all wellplates, specifying the syringe, dispense volume, dispense position, and
        how much the syringe should go down to move safely over wellplates
        """

        syringe.syringeMove(0)
        tLeftCorner, dRighCorner = self.calcWorldCor(syringe)

        for row in xrange(0, self.plateRows):
            for col in xrange(0, self.plateCols):
                if syringe.plungerPos == syringe.plungerLimit:
                    syringe.fillVolFrom(self.head, 'all', petridish)

                wellX = tLeftCorner[0] - self.wellDiameter * (row)
                wellY = tLeftCorner[1] + self.wellDiameter * (col)
                self.head.move(wellX, wellY)
                syringe.syringeMove(dispensePos)
                syringe.plungerPushVol(dispenseVol)
                syringe.syringeMove(upPos)

    def fillWell(self, syringe, wellName, dispenseVol, dispensePos, upPos):
        """
        This method fills all wellplates, specifying the syringe, dispense volume, dispense position, and
        how much the syringe should go down to move safely over wellplates
        """
        # syringe.syringeMove(0)
        tLeftCorner, dRighCorner = self.calcWorldCor(syringe)

        # length 1
        if len(wellName) == 1:
            # length 1 and int
            if wellName.isdigit():
                if int(wellName) <= self.plateCols:
                    wellY = tLeftCorner[1] + self.wellDiameter * (int(wellName) - 1)
                    for row in xrange(0, self.plateRows):
                        wellX = tLeftCorner[0] - self.wellDiameter * row
                        self.head.move(wellX, wellY)
                        syringe.syringeMove(dispensePos)
                        syringe.plungerPushVol(dispenseVol)
                        syringe.syringeMove(upPos)

                        # length 1 and char
            elif re.match("^[A-Za-z]*$", wellName):
                wellX = tLeftCorner[0] - self.wellDiameter * (ord(wellName[0].lower()) - 97)
                for col in xrange(0, self.plateCols):
                    wellY = tLeftCorner[1] + self.wellDiameter * col
                    self.head.move(wellX, wellY)
                    syringe.syringeMove(dispensePos)
                    syringe.plungerPushVol(dispenseVol)
                    syringe.syringeMove(upPos)




        # length 2
        elif len(wellName) == 2:
            # length 2 and int
            if wellName.isdigit():
                if int(wellName) <= self.plateCols:
                    wellY = tLeftCorner[1] + self.wellDiameter * (int(wellName) - 1)
                    for row in xrange(0, self.plateRows):
                        wellX = tLeftCorner[0] - self.wellDiameter * row
                        self.head.move(wellX, wellY)
                        syringe.syringeMove(dispensePos)
                        syringe.plungerPushVol(dispenseVol)
                        syringe.syringeMove(upPos)

                        # length 2 and char + int
            elif re.match("^[A-Za-z]*$", wellName[0]):
                wellX = tLeftCorner[0] - self.wellDiameter * (ord(wellName[0].lower()) - 97)
                wellY = tLeftCorner[1] + self.wellDiameter * (int(wellName[1:]) - 1)

                self.head.move(wellX, wellY)
                syringe.syringeMove(dispensePos)
                syringe.plungerPushVol(dispenseVol)
                syringe.syringeMove(upPos)



                # length 3 char + int(2 digits)
        if len(wellName) == 3:
            wellX = tLeftCorner[0] - self.wellDiameter * (ord(wellName[0].lower()) - 97)
            wellY = tLeftCorner[1] + self.wellDiameter * (int(wellName[1:]) - 1)

            self.head.move(wellX, wellY)
            syringe.syringeMove(dispensePos)
            syringe.plungerPushVol(dispenseVol)
            syringe.syringeMove(upPos)

    def calcWorldCor(self, syringe):
        if self.worldCor.syringe.syringeID <> syringe.syringeID:
            tLeftCorner = self.worldCor.worldCorFor(self.tLeftCorner, syringe)
            # dRighCorner=self.worldCor.worldCorFor(self.dRighCorner, syringe)
            dRighCorner = None

            return (tLeftCorner, dRighCorner)

        elif self.worldCor.syringe.syringeID == syringe.syringeID:
            return (self.tLeftCorner, self.dRighCorner)

    def emptyAll(self, syringe, petridish, absorbVol, absorbPos, upPos):
        """
        This method empties all wellplates, specifying the syringe, absorb volume, absorb position, and
        how much the syringe should go down to move safely over wellplates
        """

        syringe.syringeMove(0)
        tLeftCorner, dRighCorner = self.calcWorldCor(syringe)

        for row in xrange(0, self.plateRows):
            for col in xrange(0, self.plateCols):
                if syringe.plungerPos == 0:
                    syringe.emptyVolTo(self.head, 'all', petridish)

                wellX = tLeftCorner[0] - self.wellDiameter * (row)
                wellY = tLeftCorner[1] + self.wellDiameter * (col)
                self.head.move(wellX, wellY)
                syringe.syringeMove(absorbPos)
                syringe.plungerPullVol(absorbVol)
                syringe.syringeMove(upPos)
        syringe.emptyVolTo(self.head, 'all', petridish)

    def transferToWellplate(self, syringe, wellplate, absorbVol, absorbPos, upPos):
        """
        This method empties all wellplates, specifying the syringe, absorb volume, absorb position, and
        how much the syringe should go down to move safely over wellplates
        """

        syringe.syringeMove(0)
        tLeftCorner, dRighCorner = self.calcWorldCor(syringe)

        tLeftCorner2, dRighCorner2 = wellplate.calcWorldCor(syringe)

        for row in xrange(0, self.plateRows):
            for col in xrange(0, self.plateCols):
                if syringe.plungerPos == 0:
                    print 'syringe full, not able to absorb'
                    # syringe.emptyVolTo(self.head, 'all', petridish)

                wellX = tLeftCorner[0] - self.wellDiameter * (row)
                wellY = tLeftCorner[1] + self.wellDiameter * (col)
                self.head.move(wellX, wellY)
                syringe.syringeMove(absorbPos)
                syringe.plungerPullVol(absorbVol)
                syringe.syringeMove(upPos)

                well2X = tLeftCorner2[0] - self.wellDiameter * (row)
                well2Y = tLeftCorner2[1] + self.wellDiameter * (col)
                self.head.move(well2X, well2Y)
                syringe.syringeMove(absorbPos)
                syringe.plungerPushVol(absorbVol)
                syringe.syringeMove(upPos)
