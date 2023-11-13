import time
import threading
import datetime
import sys
from worldcor import WorldCor


class PetriDish:
    def __init__(self, _evobot, center, goalPos, diameter=110, edgeHeight=20, volume=100, liquidType='undefined',
                 worldCor=None, clean_flag=True):
        """
        This method initialize the petridish object.
        """
        self.center = center
        self.goalPos = goalPos
        self.diameter = diameter
        self.volume = volume
        self.liquidType = liquidType
        self.evobot = _evobot
        self.dateLogger = None
        self.worldCor = worldCor
        self.edgeHeight = edgeHeight
        self.clean_flag = clean_flag

    def is_clean(self):
        return self.clean_flag

    # def set_flag(self):
    #     self.clean_flag = True
