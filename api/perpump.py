import datetime
import time
import threading
from configuration import *
import datalogger, math

class Perpump:
    '''
    This class contains functions for peristaltic pump control.
    '''
    def __init__(self, _evobot):
        self.evobot = _evobot
    def start(self):
        self.evobot._logUsrMsg('The perpump is on')
        self.evobot.send("M286 D9 V1")
    def stop(self):
        self.evobot._logUsrMsg('The perpump is off')
        self.evobot.send("M286 D9 V0")
    def time_run(self):
         self.evobot.send("M286 D9 T{}".format(time_run_value))

'''
    def zk(self):
        print("T{}".format(value))

value = 6
Perpump.zk(value)
'''       