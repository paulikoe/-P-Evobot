import datetime
import math
import time
import cv2
import numpy as np
import VisionTools as vT
from beaker_coordinates import *
from head import Head
from multiDropletTracking import MultiDropletTracking
from petri_dish_coordinates import petri_dish_coord
from pump import Pump
from syringe import Syringe
from worldcor import WorldCor
from datalogger import DataLogger
from evobot import EvoBot
from petridish import PetriDish
import sys
import os
from dispenser import Dispenser
from servo import Servo

sys.path.append('../../api')
sys.path.append('../../settings')
from configuration import *

# droplet decanol (volumes)

distance_from_center = 20.0  # distance from the center of the petridish to pull decanol and salt
park_head_pos = (0, 0)
park_head_pos_different_individual = (0, 450)
reagent_plunger_fast_speed = 90
air_volume_reagent = 1.8
# video recording variables
date = ""
fourCC = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # for mac user
# fourCC = cv2.VideoWriter_fourcc(*'XVID')  # use this in windows
recording = True  # This activates the recording of the experiment

# This resolution should be the camera resolution
window_size = (1280, 720)
experiment_time = 120  # in seconds
cap = cv2.VideoCapture(CAMERA_ID)
# Name for the datalogger
fileName = time.strftime("%Y-%m-%d %H%M%S")


def _calculate_pitagora(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2.0) + ((a[1] - b[1]) ** 2.0))


def transform_matrices(module_matrix):
    """This function transform the matrices of the modules"""
    module_matrix_transformed = cv2.invertAffineTransform(module_matrix)
    return module_matrix_transformed


class NewReagentsExperiments:
    """ Evolutionary experiment class, it has functions for performing recording of experiments with
     decanoate, decanol and salt """

    def __init__(self):
        """Init function used to initialize all the variables"""
        self.usrmsglogger = DataLogger()
        self.evobot = EvoBot(PORT_NO, self.usrmsglogger)
        self.head = Head(self.evobot)
        self.headLogger = DataLogger('experiments/head' + fileName, kind='csv')
        self.head.setSpeed(7000)
        os.system("say 'Hello, I am going to prepare all the syringes, it is gonna take a while, "
                  "you relax in the meanwhile'")

        # decanol syringe
        self.decanol_syringe = Syringe(self.evobot, SYRINGES['SYRINGE4'])
        # self.decanol_syringe.home()
        self.decanol_syringe.plungerMoveToDefaultPos()
        self.decanol_syr_coord = WorldCor(self.decanol_syringe, mode='default')

        # salt syringe
        self.salt_syringe = Syringe(self.evobot, SYRINGES['SYRINGE11'])
        self.salt_syringe.plungerSetAcc(90)
        # self.salt_syringe.home()
        self.salt_syringe.plungerMoveToDefaultPos()
        self.salt_syringe.plungerSetSpeed(50)
        self.salt_syringe.plungerSetAcc(40)

        # reagent syringe
        self.reagent_syringe = Syringe(self.evobot, SYRINGES['SYRINGE1'])
        # self.reagent_syringe.home()
        self.reagent_syringe.plungerSetSpeed(reagent_plunger_fast_speed)
        self.reagent_syringe.plungerMoveToDefaultPos()
        self.syringeLogger = DataLogger('experiments/syringe' + fileName)
        self.reagent_syringe.dataLogger = self.syringeLogger
        self.head.home()

        # Set the decanoate syringe as the coordinate system of the program
        self.reagent_syr_coord = WorldCor(self.reagent_syringe, mode='default')
        self.waste_container = PetriDish(self.evobot, center=petri_dish_coord['waste'], goalPos=-30,
                                         liquidType='waster', diameter=90, worldCor=self.reagent_syr_coord)
        self.clean_container = PetriDish(self.evobot, center=petri_dish_coord['clean_water'], goalPos=-30,
                                         liquidType='water', diameter=90, worldCor=self.reagent_syr_coord)

        # self.servo_syringe = Dispenser(self.evobot, SYRINGES['SYRINGE0'])
        # self.servo_syringe.home_dispenser()
        #
        # # Instantiate servo object
        # self.servo = Servo(self.evobot, SERVOS['SERVO2'])
        # self.servo.servo_home()

    @staticmethod
    def mask_frame(frame, x_center, y_center, radius):
        height, width, _ = frame.shape
        mask = np.zeros((height, width, 3), np.uint8)
        mask.fill(0)
        cv2.circle(mask, (x_center, y_center), radius, (255, 255, 255), -1)
        frame = cv2.bitwise_and(frame, mask)
        return frame

    def decanol_pull(self, dec_vol):
        """This function pulls the decanol droplet from the stock of decanol"""
        self.head.move(decanol['decanol_stock'][0], decanol['decanol_stock'][1])
        if self.decanol_syringe.canAbsorbVol(dec_vol):
            self.decanol_syringe.syringeSetSpeed(90)
            # self.decanol_syringe.syringeSetAcc(200)
            self.decanol_syringe.syringeMove(-67)
            self.decanol_syringe.plungerPullVol(dec_vol)
            self.decanol_syringe.homeSyringe()

        else:
            print "volume exceeds capacity"

    def decanol_push(self, petridish, dec_vol):
        """This function pushes the decanol droplet in the petridish"""
        (x_p, y_p) = self.decanol_syr_coord.worldCorFor((petridish.center[0], petridish.center[1]),
                                                        self.decanol_syringe)
        self.head.move(x_p, y_p + distance_from_center)
        self.decanol_syringe.syringeSetSpeed(50)
        self.decanol_syringe.syringeMove(self.decanol_syringe.syringeGoalPos)
        time.sleep(1)
        self.decanol_syringe.plungerSetSpeed(10)
        self.decanol_syringe.plungerPushVol(dec_vol)
        time.sleep(4)
        self.decanol_syringe.syringeSetSpeed(120)
        self.decanol_syringe.homeSyringe()
        print "the decanol was pushed in %s" % ((x_p, y_p + distance_from_center),)
        return x_p, y_p + distance_from_center

    def salt_pull(self, salt_vol):
        """This function pulls the salt from the salt stock"""
        self.head.move(salt['salt_stock'][0], salt['salt_stock'][1])
        if self.salt_syringe.canAbsorbVol(salt_vol):
            self.salt_syringe.plungerSetSpeed(150)
            self.salt_syringe.syringeMove(-75)
            self.salt_syringe.plungerPullVol(salt_vol)
            self.salt_syringe.plungerSetSpeed(30)
            self.salt_syringe.homeSyringe()

        else:
            print "volume exceeds capacity"

    def salt_push(self, petridish, salt_vol):
        """This function pushes the salt in the salt point in the petridish"""
        # (x_p, y_p) = self.decanol_syr_coord.worldCorFor((petridish.center[0], petridish.center[1]), self.salt_syringe)
        (x_p, y_p) = petridish.center[0], petridish.center[1]
        self.head.move(x_p-50, y_p - distance_from_center)
        self.salt_syringe.plungerSetSpeed(30)
        self.salt_syringe.syringeMove(self.salt_syringe.syringeGoalPos)
        self.salt_syringe.plungerPushVol(salt_vol)
        self.salt_syringe.homeSyringe()
        self.salt_syringe.plungerSetSpeed(100)
        print "the salt was pushed in %s in salt coordinates" % ((x_p-50, (y_p - distance_from_center)),)

    def get_reagent(self, x, y, volume_amount, petridish, syringe_height):

        """This function PULL and PUSH the reagent solution into the petridish"""

        # get decanoate solution
        # (x_p, y_p) = self.decanol_syr_coord.worldCorFor((petridish.center[0], petridish.center[1]),
        #                                                 self.reagent_syringe)
        (x_p, y_p ) = (petridish.center[0]-70, petridish.center[1]-150)
        self.head.move(x, y)
        self.reagent_syringe.plungerPullVol(air_volume_reagent)
        self.reagent_syringe.syringeMove(syringe_height)
        self.reagent_syringe.plungerPullVol(volume_amount)
        self.reagent_syringe.homeSyringe()

        print "reagent collected"
        # dispense decanoate in the petridish
        self.head.move(x_p, y_p)
        self.reagent_syringe.syringeMove(-30)
        self.reagent_syringe.continuous_dispensation_of_liquid(self.head, (x_p, y_p),
                                                               volume_amount + air_volume_reagent,
                                                               radius=30, radius_max=39)
        self.reagent_syringe.homeSyringe()
        self.reagent_syringe.plungerSetSpeed(reagent_plunger_fast_speed)
        print 'reagent poured in petridish'

    def prepare_experiment(self, exp_petridish, reagent_name):
        """This function prepare the environment (liquids) for the experiment according to values of the individual
        to evaluate """

        final_volume = 10.8

        reagent_position = reagent_bakers_coord[reagent_name]

        print "---> Adding reagent %s to the petridish" % reagent_name

        os.system("say 'Adding reagent %s to the petridish'" % reagent_name)
        self.get_reagent(reagent_position[0], reagent_position[1], final_volume, exp_petridish, syringe_height=-70)

        print "---> Washing the syringe"
        os.system("say 'washing the syringe'")
        self.reagent_syringe.syringe_wash(self.head, self.waste_container, self.clean_container, times=1,
                                          volume_clean_liquid=5)

    def perform_experiment(self, petri, gen, individual_num, reagent_name, replica_num):
        """This function starts the experiment on the petri given as arguments, called in the ga-dropletTrack.py file"""

        global frame_droplet_left_safe, end_tracking_time
        import os
        salt_volume = 0.3
        decanol_volume = 0.025

        # cv2.namedWindow('Window')
        # cv2.startWindowThread()

        cap.set(3, window_size[0])
        cap.set(4, window_size[1])
        ret, frame = cap.read()
        if ret == 0:
            print 'ERROR READING INPUT'

        x = petri.center[0]
        y = petri.center[1]
        radius_pix = 132

        # the coordinates need to be transformed in order to be used for the mask
        self.x_in_pixels = int(self.decanol_syr_coord.mmTopix((x, y))[0])
        self.y_in_pixels = int(self.decanol_syr_coord.mmTopix((x, y))[1])

        os.system("say 'Pulling salt'")
        print "Pulling salt"

        self.salt_pull(salt_volume)

        os.system("say 'Pulling decanol'")
        print "Pulling decanol"

        self.decanol_pull(decanol_volume)

        os.system("say 'Pushing decanol'")
        print "Pushing decanol"
        decanol_start = self.decanol_push(petri, decanol_volume)
        # decanol_start = (20, 20)

        self.head.setSpeed(3000)
        os.system("say 'Pushing salt'")
        print "Pushing salt"
        self.salt_push(petri, salt_volume)
        self.head.setSpeed(5000)
        salt_destination = (decanol_start[0], decanol_start[1] - (2.0 * distance_from_center))  # mm

        # Salt pos in pixels
        salt_x_in_pixels = int(self.decanol_syr_coord.mmTopix((salt_destination[0], salt_destination[1]))[0])
        salt_y_in_pixels = int(self.decanol_syr_coord.mmTopix((salt_destination[0], salt_destination[1]))[1])

        salt_destination_pixel = (salt_x_in_pixels, salt_y_in_pixels)

        # park the head in different positions according to the number of experiment that is performing

        # if individual_num != 4 or individual_num != 12:
        #     self.head.move(park_head_pos[0], park_head_pos[1])
        # else:
        #     self.head.move(park_head_pos_different_individual[0], park_head_pos_different_individual[1])

        # self.servo.servoMove(30)
        # self.servo_syringe.dispenser_move(-29)

        modality = "tracking"

        os.system("say 'Starting tracking'")
        print "TRACKING MODE entered."
        # We start an exp!!!
        file_name_addition = "sat_generation%d_ind_num%d_replica%d_reagent:%s" % (gen, individual_num, replica_num, reagent_name)

        if recording:
            date = str(datetime.datetime.now())
            file_name = os.path.join(FILE_PATH, "%s_video.mp4" % vT.removeColon(date + file_name_addition))
            out = cv2.VideoWriter(file_name, fourCC, 10.0, window_size)

        start_tracking_time = datetime.datetime.now()

        while True:
            ret, frame = cap.read()  # Read a new frame from the camera
            if ret == 0:
                print "ERROR READING INPUT"

            # Make a copy of the current frame
            result = frame.copy()

            # Draw a circle around the Petri dish object
            # cv2.circle(result, (self.x_in_pixels, self.y_in_pixels), radius_pix, (0, 0, 255), 2)
            frame = self.mask_frame(frame, self.x_in_pixels, self.y_in_pixels, radius_pix)

            # cv2.circle(result, salt_destination_pixel, 10, (0, 255, 0), 1)

            # OPTIONS
            # Waits up to other 30ms for a keypress
            # If none -> -1
            key = cv2.waitKey(30) & 0xFF
            now = datetime.datetime.now()

            done_tracking = modality == "tracking" and (
                (start_tracking_time + datetime.timedelta(seconds=experiment_time)) <= now)

            if done_tracking:
                print "Stop", done_tracking, start_tracking_time, now
                break
            elif key == ord('q'):
                # If q is pressed, quit
                print "Aborted", done_tracking, start_tracking_time, now
                break

            if modality == "tracking":
                cv2.putText(result, "TRACKING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
                cv2.putText(result,
                            "generation: %d, ind_num: %d, replica: %d" %
                            (gen, individual_num, replica_num),
                            (150, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255))

            if recording:
                out.write(result)
                cv2.putText(result, "RECORDING", (150, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)

        # END WHILE TRUE
        # self.servo_syringe.home()
        # self.servo.servo_home()
        fitness_value = 0.0
        print 'the coordinates of the center of the petridish are: ' + str((x, y), )

        return fitness_value

    def quit(self):
        self.evobot.disconnect()
        self.head.dataLogger.file.close()
        self.reagent_syringe.dataLogger.file.close()



