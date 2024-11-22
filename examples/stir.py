import time
import sys
import math

sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from head import Head
from datalogger import DataLogger


usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head( evobot ) 
R = 40

head.move( 90, 100 )
while True:
    for itr in range(1,360):
        angle = (float(itr) / float( 360 )) * float( 2*math.pi )
        head.moveContinously( round( 50 + R*math.cos( angle),2), round( 100 + R*math.sin( angle ) , 2))
