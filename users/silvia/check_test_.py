import sys
import time
sys.path.append('../api')
sys.path.append('../settings')
import cv2
from users.silvia.petri_dish_coordinates import petridishes
from local import *
from syringe import Syringe
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
from servo import Servo
from worldcor import WorldCor
import numpy as np
import datetime
from dispenser import Dispenser
from pump import Pump
from syringe import Syringe
#
usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)

# head.setSpeed(9000)
# head.move(41, 173)
# head.setSpeed(3000)
# head.move(0, 0)

# s1_syringe = Syringe(evobot, SYRINGES['SYRINGE1'])
# s1_syringe.plungerMoveToDefaultPos()
# s1_syringe.plungerPullVol(1)

pump_syringe = Pump(evobot, PUMPS['PUMP1'])
pump_syringe.setSpeed(200)
# pump_syringe.continuous_dispensation_of_liquid((40, 100), 20, 40)
pump_syringe.pumpPullVol(10)

# decanoate_syringe = Syringe(evobot, SYRINGES['SYRINGE1'])
# decanoate_syringe.plungerMoveToDefaultPos()
# decanoate_syringe.plungerPushVol(10)
# decanoate_syringe.syringeMove(-30)
# decanoate_syringe.continuous_dispensation_of_liquid(head, (140, 42), 8, radius=20, radius_max=30)



# head.move(100, 100)

# air_volume_decanoate = 1.8
# syringe_height = -70
# volume_amount = 5.0

# fin_vol = volume_amount+0.01
# print fin_vol
#
# s1_syringe = Syringe(evobot, SYRINGES['SYRINGE1'])
# s1_syringe.plungerMoveToDefaultPos()
# s1_syringe.homeSyringe()
# head.move(23, 499)
# # s1_syringe.plungerPullVol(air_volume_decanoate)
# # s1_syringe.syringeMove(syringe_height)
# # s1_syringe.plungerPullVol(volume_amount)
# # s1_syringe.homeSyringe()
# head.move(135.3, 37.4)
# s1_syringe.syringeMove(s1_syringe.syringeGoalPos)
# time.sleep(4)
# # s1_syringe.syringeMove(-30)
#
# # s1_syringe.plungerPushVol(volume_amount+air_volume_decanoate)
# s1_syringe.homeSyringe()


# s1_syringe.continuous_dispensation_of_liquid(head, (135.3, 37.4), volume_amount + air_volume_decanoate, radius=30,
#                                              radius_max=40)


# for i in range(0, 10):
#     i += 1
#     s1_syringe.plungerPullVol(0.9)
#     s1_syringe.plungerPushVol(0.9)


# s1_syringe = Syringe(evobot, SYRINGES['SYRINGE4'])
# head.move(134, 67)
# s1_syringe.syringeMove(-69)
# s1_syringe.plungerPullVol(0.05)
# s1_syringe.homeSyringe()
# head.move(194, 147)
# s1_syringe.syringeMove(s1_syringe.syringeGoalPos)
# s1_syringe.plungerPushVol(0.03)
# time.sleep(3)
# s1_syringe.homeSyringe()

from beaker_coordinates import *
# decanol_volume = 0.015
#
# s4_syringe = Syringe(evobot, SYRINGES['SYRINGE1'])
# s4_syringe.homeSyringe()
#
#
# s4_syringe.syringe_wash(head, waste_container, self.clean_container, times=1,
#                                           volume_clean_liquid=5)
#
#

# servo = Servo(evobot, SERVOS['SERVO2'])
# servo_syringe = Dispenser(evobot, SYRINGES['SYRINGE0'])
#
#
# servo.servoMove(47)  # TODO: check this movements
# servo_syringe.dispenser_move(-26)
# time.sleep(20)
# servo_syringe.home()
# servo.servo_home()

#
# servo_syringe.home()
# servo.servoMove(30)
# time.sleep(2)
# head.move(100, 220)
# servo.servoMove(0)
# servo_syringe.dispenser_move(-29)
# time.sleep(4)
# servo_syringe.home()
# servo.servo_home()
#
#
# head.home()
# servo.servoMove(servo.goal_pos)
# servo_syringe.dispenser_move(-20)

# servo.servo_home()

# head.home()

# decanol_syringe = Syringe(evobot, SYRINGES['SYRINGE4'])
# dec_vol= 0.025
# head.move(decanol['decanol_stock'][0], decanol['decanol_stock'][1])
# decanol_syringe.syringeSetSpeed(90)
#
# decanol_syringe.syringeMove(-67)
# decanol_syringe.plungerPullVol(dec_vol)
# decanol_syringe.homeSyringe()

evobot.disconnect()



