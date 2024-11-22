import sys

sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head
from petridish import PetriDish
from calibration import Calibration

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)
head.setSpeed(7000)

syringe1 = Syringe(evobot, SYRINGES['SYRINGE1'])
syringe4 = Syringe(evobot, SYRINGES['SYRINGE4'])
syringe11 = Syringe(evobot, SYRINGES['SYRINGE11'])

petridish = PetriDish(evobot, center=(39, 281), goalPos=-67, diameter=9, liquidType='water')

# use this calibration object if you want to calibrate with a petri dish
# calibration = Calibration(evobot, head, petridish=petridish, syringe=syringe1)

# use this if you need to use 3 custom points for calibration (e.g. the experimental layer is big)

# calibration = Calibration(evobot, head, customPoints=([10, 0], [161, 0], [141, 372]), syringe=syringe1)
# calibration = Calibration(evobot, head, customPoints=([55, 150], [190, 150], [130, 475]), syringe=syringe4)
calibration = Calibration(evobot, head, customPoints=([40, 140], [140, 140], [137, 515]), syringe=syringe11)
#

calibration.affineCalibrate()
