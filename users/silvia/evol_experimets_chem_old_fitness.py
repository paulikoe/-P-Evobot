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

sys.path.append('../../api')
sys.path.append('../../settings')
from configuration import *

# droplet decanol (volumes)

distance_from_center = 20.0  # distance from the center of the petridish to pull decanol and salt
park_head_pos = (0, 0)
park_head_pos_different_individual = (0, 450)
decanoate_plunger_fast_speed = 90
air_volume_decanoate = 1.8
# video recording variables
date = ""
fourCC = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # for mac user
# fourCC = cv2.VideoWriter_fourcc(*'XVID')  # use this in windows
recording = True  # This activates the recording of the experiment

# This resolution should be the camera resolution
window_size = (1280, 720)
experiment_time = 60  # in seconds
cap = cv2.VideoCapture(CAMERA_ID)
# Name for the datalogger
fileName = time.strftime("%Y-%m-%d %H%M%S")


def compute_volumes(x_sol_ph, y_sol_ph, final_molarity, final_ph):
    """This function returns the volumes of the two solutions of decanoate to be mixed in L"""
    x_molarity = 20.e-3  # in M
    final_volume_l = 10.e-3  # in liters
    h2o_ph = 6.
    f = final_molarity * 10 ** (-3)  # in M
    print f
    final_oh_concentration = 1.0 / (10. ** (14. - final_ph))
    x_oh_concentration = 1.0 / (10. ** (14. - x_sol_ph))
    y_oh_concentration = 1.0 / (10. ** (14. - y_sol_ph))
    h2o_oh_concentration = 1.0 / (10. ** (14. - h2o_ph))
    print 'PH PRIMA SOLUZIONE: %d' % x_sol_ph
    print 'PH SECONDA SOLUZIONE: %d' % y_sol_ph

    y_vol = (final_oh_concentration * final_volume_l + (f * final_volume_l / x_molarity) * h2o_oh_concentration -
             (f * final_volume_l / x_molarity) * x_oh_concentration - final_volume_l * h2o_oh_concentration) / \
            (y_oh_concentration - x_oh_concentration)
    x_vol = ((f * final_volume_l) / x_molarity) - y_vol
    if x_vol < 0:
        if y_sol_ph < 13:
            x_vol, y_vol = compute_volumes(x_sol_ph, y_sol_ph + 1, final_molarity, final_ph)
        else:
            sys.exit("volume is negative. x_vol = " + str(x_vol) + ", y_vol=" + str(y_vol))
    elif y_vol < 0:
        if x_sol_ph > 7:
            x_vol, y_vol = compute_volumes(x_sol_ph - 1, y_sol_ph, final_molarity, final_ph)
        else:
            sys.exit("volume is negative. x_vol = " + str(x_vol) + ", y_vol=" + str(y_vol))
    return x_vol, y_vol


def _calculate_pitagora(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2.0) + ((a[1] - b[1]) ** 2.0))


def transform_matrices(module_matrix):
    """This function transform the matrixes of the modules"""
    module_matrix_transformed = cv2.invertAffineTransform(module_matrix)
    return module_matrix_transformed


class EvolutionaryExperimentOldFitness:
    """ Evolutionary experiment class, it has functions for performing evolutionary experiments with
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

        # pump for water
        self.water_pump = Pump(self.evobot, PUMPS['PUMP1'])
        self.water_pump.setSpeed(100)
        # dispenser for water
        self.water_syringe = Dispenser(self.evobot, SYRINGES['SYRINGE15'])
        self.water_syringe.home_dispenser()

        # decanol syringe
        self.decanol_syringe = Syringe(self.evobot, SYRINGES['SYRINGE4'])
        self.decanol_syringe.home()
        self.decanol_syringe.plungerMoveToDefaultPos()
        self.decanol_syr_coord = WorldCor(self.decanol_syringe, mode='default')

        # salt syringe
        self.salt_syringe = Syringe(self.evobot, SYRINGES['SYRINGE11'])
        self.salt_syringe.plungerSetAcc(90)
        self.salt_syringe.home()
        self.salt_syringe.plungerMoveToDefaultPos()
        self.salt_syringe.plungerSetSpeed(50)
        self.salt_syringe.plungerSetAcc(40)

        self.decanoate_syringe = Syringe(self.evobot, SYRINGES['SYRINGE1'])
        self.decanoate_syringe.home()
        self.decanoate_syringe.plungerSetSpeed(decanoate_plunger_fast_speed)
        self.decanoate_syringe.plungerMoveToDefaultPos()
        self.syringeLogger = DataLogger('experiments/syringe' + fileName)
        self.decanoate_syringe.dataLogger = self.syringeLogger
        self.head.home()

        # Set the decanoate syringe as the coordinate system of the program
        self.decanoate_syr_coord = WorldCor(self.decanoate_syringe, mode='default')
        self.waste_container = PetriDish(self.evobot, center=petri_dish_coord['waste'], goalPos=-30,
                                         liquidType='waster', diameter=90, worldCor=self.decanoate_syr_coord)
        self.clean_container = PetriDish(self.evobot, center=petri_dish_coord['clean_water'], goalPos=-30,
                                         liquidType='water', diameter=90, worldCor=self.decanoate_syr_coord)

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
            self.decanol_syringe.syringeMove(-69)
            self.decanol_syringe.plungerPullVol(dec_vol)
            self.decanol_syringe.homeSyringe()

        else:
            print "volume exceeds capacity"

    def decanol_push(self, petridish, dec_vol):
        """This function pushes the decanol droplet in the petridish"""
        (x_p, y_p) = self.decanol_syr_coord.worldCorFor((petridish.center[0], petridish.center[1]),
                                                        self.decanol_syringe)
        self.head.move(x_p, y_p + distance_from_center)
        self.decanol_syringe.syringeSetSpeed(90)
        self.decanol_syringe.syringeMove(self.decanol_syringe.syringeGoalPos)
        self.decanol_syringe.plungerPushVol(dec_vol)
        time.sleep(2)
        self.decanol_syringe.syringeSetSpeed(120)
        self.decanol_syringe.homeSyringe()
        print "the decanol was pushed in %s" % ((x_p, y_p + distance_from_center),)
        return x_p, y_p + distance_from_center

    def salt_pull(self, salt_vol):
        """This function pulls the salt from the salt stock"""
        self.head.move(salt['salt_stock'][0], salt['salt_stock'][1])
        if self.salt_syringe.canAbsorbVol(salt_vol):
            self.salt_syringe.syringeMove(-75)
            self.salt_syringe.plungerPullVol(salt_vol)
            self.salt_syringe.homeSyringe()

        else:
            print "volume exceeds capacity"

    def salt_push(self, petridish, salt_vol):
        """This function pushes the salt in the salt point in the petridish"""
        (x_p, y_p) = self.decanol_syr_coord.worldCorFor((petridish.center[0], petridish.center[1]), self.salt_syringe)
        self.head.move(x_p, y_p - distance_from_center)
        self.salt_syringe.plungerSetSpeed(40)
        self.salt_syringe.syringeMove(self.salt_syringe.syringeGoalPos)
        self.salt_syringe.plungerPushVol(salt_vol)
        self.salt_syringe.homeSyringe()
        self.salt_syringe.plungerSetSpeed(144)
        print "the salt was pushed in %s in salt coordinates" % ((x_p, y_p - distance_from_center),)

    def add_water(self, water_amount, petridish):
        """ This function pull and push water from the pump in the petridish """
        # dispense water
        (x_p, y_p) = self.decanol_syr_coord.worldCorFor((petridish.center[0], petridish.center[1]), self.water_syringe)
        self.head.move(x_p, y_p)
        self.water_syringe.dispenser_move(-40)
        self.water_pump.pumpPushVol(water_amount)
        # self.water_pump.continuous_dispensation_of_liquid((x_p, y_p), water_amount, 40)
        self.water_syringe.home_dispenser()
        print 'the water was poured in the petridish'

    def get_decanoate(self, x, y, volume_amount, petridish, syringe_height):
        """This function PULL and PUSH decanoate solutions into the petridish"""
        # get decanoate solution
        (x_p, y_p) = self.decanol_syr_coord.worldCorFor((petridish.center[0], petridish.center[1]),
                                                        self.decanoate_syringe)
        self.head.move(x, y)
        self.decanoate_syringe.plungerPullVol(air_volume_decanoate)
        self.decanoate_syringe.syringeMove(syringe_height)
        self.decanoate_syringe.plungerPullVol(volume_amount)
        self.decanoate_syringe.homeSyringe()

        print "decanoate collected"
        # dispense decanoate in the petridish
        self.head.move(x_p, y_p)
        self.decanoate_syringe.syringeMove(-30)
        self.decanoate_syringe.continuous_dispensation_of_liquid(self.head, (x_p, y_p),
                                                                 volume_amount + air_volume_decanoate,
                                                                 radius=30, radius_max=39)
        self.decanoate_syringe.homeSyringe()
        self.decanoate_syringe.plungerSetSpeed(decanoate_plunger_fast_speed)
        print 'decanoate poured in petridish'

    def prepare_experiment(self, decanoate_solution, exp_petridish):
        """This function prepare the environment (liquids) for the experiment according to values of the individual
        to evaluate """
        ph, molarity = decanoate_solution
        # ph_real = 7 + ((12.3 - 7) * ph)  # give me a number between 7 and 12.3 with decimals
        ph_real = 7 + (5 * ph)  # give me a number between 7 and 12 with decimals - changed for exhaustive search
        mol_real = 5 + ((20 - 5) * molarity)  # give me a number between 5 and 20
        print "Evaluation of the individual (pH parameter is " + str(ph_real) + " and molarity parameter is " + str(
            mol_real) + ")"
        final_volume = 9.

        x_sol_ph = math.floor(ph_real)
        y_sol_ph = x_sol_ph + 1
        x_vol, y_vol = compute_volumes(x_sol_ph, y_sol_ph, mol_real, ph_real)
        x_vol = round(x_vol * 1000, 2)
        y_vol = round(y_vol * 1000, 2)

        print 'VALUES OF VOLUMES OF DECANOATE: ' + str((x_vol, y_vol))

        h20_volume = final_volume - (x_vol + y_vol)

        if h20_volume < 0:
            h20_volume = 0

        print 'VOLUME OF WATER: ' + str(h20_volume)
        x_sol_position = decanoate_bakers_coord[x_sol_ph]
        y_sol_position = decanoate_bakers_coord[y_sol_ph]

        print "---> Adding water in the petridish"
        os.system("say 'Adding water in the petridish'")

        self.add_water(h20_volume, exp_petridish)

        print "---> Adding first decanoate solution with pH %f to the petridish" % x_sol_ph
        os.system("say 'Adding first decanoate solution'")
        self.get_decanoate(x_sol_position[0], x_sol_position[1], x_vol, exp_petridish, syringe_height=-70)

        print "---> Washing the syringe"
        os.system("say 'washing the syringe'")
        self.decanoate_syringe.syringe_wash(self.head, self.waste_container, self.clean_container, times=1,
                                            volume_clean_liquid=5)

        print "---> Adding second decanoate solution with pH %f to the petridish" % y_sol_ph
        os.system("say 'Adding second decanoate solution'")
        self.get_decanoate(y_sol_position[0], y_sol_position[1], y_vol, exp_petridish, syringe_height=-70)

        print '---> Mixing solutions'
        os.system("say 'Mixing solutions'")
        (x_p, y_p) = self.decanol_syr_coord.worldCorFor((exp_petridish.center[0], exp_petridish.center[1]),
                                                        self.decanoate_syringe)
        self.decanoate_syringe.mixing_up_liquids_(self.head, x_p, y_p, volume_to_mix=4, air_volume=air_volume_decanoate,
                                                  syringe_height=-42, rounds=3)

        print "---> Washing the syringe"
        os.system("say 'washing the syringe'")
        self.decanoate_syringe.syringe_wash(self.head, self.waste_container, self.clean_container, times=1,
                                            volume_clean_liquid=5)

        return ph_real, mol_real

    def perform_experiment(self, petri, ph, molarity, gen, individual_num, replica_num):
        """This function starts the experiment on the petri given as arguments, called in the ga-dropletTrack.py file"""

        global frame_droplet_left_safe
        import os
        salt_volume = 0.3
        decanol_volume = 0.03

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

        if individual_num != 4:
            self.head.move(park_head_pos[0], park_head_pos[1])
        else:
            self.head.move(park_head_pos_different_individual[0], park_head_pos_different_individual[1])

        # park the head in different positions according to number of individual and the number of replica performing

        # if individual_num != 1 and replica_num != 1 | \
        #         individual_num != 4 and replica_num != 0 | \
        #         individual_num != 6 and replica_num != 2:
        #     self.head.move(park_head_pos[0], park_head_pos[1])
        # else:
        #     self.head.move(park_head_pos_different_individual[0], park_head_pos_different_individual[1])

        modality = "tracking"

        os.system("say 'Starting tracking'")
        print "TRACKING MODE entered."
        # We start an exp!!!
        file_name_addition = "generation%d_ind_num%d_ph%f_mol%f_replica%d" % (gen, individual_num, ph, molarity, replica_num)

        if recording:
            date = str(datetime.datetime.now())
            file_name = os.path.join(FILE_PATH, "%s_video.mp4" % vT.removeColon(date + file_name_addition))
            out = cv2.VideoWriter(file_name, fourCC, 10.0, window_size)

        start_tracking_time = datetime.datetime.now()
        track2 = MultiDropletTracking()
        # For the analysis of the path, variable that indicates if the droplet has left the safe area
        left_safe_area = False
        counter = 0.0
        frame_counter = 0.0

        while True:
            ret, frame = cap.read()  # Read a new frame from the camera
            if ret == 0:
                print "ERROR READING INPUT"

            # Make a copy of the current frame
            result = frame.copy()

            # Draw a circle around the Petri dish object
            cv2.circle(result, (self.x_in_pixels, self.y_in_pixels), radius_pix, (0, 0, 255), 2)
            frame = self.mask_frame(frame, self.x_in_pixels, self.y_in_pixels, radius_pix)

            track2.do_track(frame, result)

            #  Analysis of the path #

            # Radius of the safe are around the starting position where the direction of the droplet is irrelevant
            radius_start = 30
            analysis_frame = 8  # Number of frames between the current pos and the pos used to calculate the direction
            # Max angle that is allowed between the (droplet direction angle) and (droplet-salt angle)
            angle_threshold = 55.0 / 180.0 * math.pi

            distance_threshold = 6.0
            frame_droplet_left_safe = 0  # Var used to indicate the frame where the droplet leaves the safe area

            # Get path
            path = track2.get_biggest_path()

            # Get start coordinates and draw a circle around the start and final position
            start_coordinates = path[0]
            cv2.circle(result, start_coordinates, radius_start, (0, 255, 0), 1)
            cv2.circle(result, salt_destination_pixel, 10, (0, 255, 0), 1)

            # If we are in the safe area, do nothing
            current_pos = path[len(path) - 1]
            distance_from_start_point = _calculate_pitagora(current_pos, start_coordinates)
            if distance_from_start_point < radius_start and not left_safe_area:
                frame_droplet_left_safe = len(path) - 1
            else:
                # The droplet has abandoned the safe area
                left_safe_area = True
                if len(path) - 1 - analysis_frame - frame_droplet_left_safe > -1:
                    # There are enough frames after the droplet left the safe area
                    last_pos = path[len(path) - 1 - analysis_frame]
                    moved_dist = _calculate_pitagora(current_pos, last_pos)
                    curr_dir = math.atan2(current_pos[1] - last_pos[1], current_pos[0] - last_pos[0])
                    salt_dir = math.atan2(salt_destination[1] - last_pos[1], salt_destination[0] - last_pos[0])
                    angle_dif = curr_dir - salt_dir
                    if angle_dif > math.pi:
                        angle_dif -= 2.0 * math.pi
                    if angle_dif < -math.pi:
                        angle_dif += 2.0 * math.pi
                    # print str(round(curr_dir * 180.0 / math.pi, 1)) + "\t" + str(
                    #     round(salt_dir * 180.0 / math.pi, 1)) + "\t" + str(
                    #     round(angle_dif * 180.0 / math.pi, 1)) + "\t" + str(moved_dist)
                    if abs(angle_dif) > angle_threshold and moved_dist > distance_threshold:
                        print "Aborted, droplet is not going towards the salt"
                        end_tracking_time = datetime.datetime.now()
                        break
                    # END OF ANALYSIS OF THE PATH #

            # OPTIONS
            # Waits up to other 30ms for a keypress
            # If none -> -1
            key = cv2.waitKey(30) & 0xFF
            now = datetime.datetime.now()

            done_tracking = modality == "tracking" and (
                (start_tracking_time + datetime.timedelta(seconds=experiment_time)) <= now)

            if done_tracking:
                print "Stop", done_tracking, start_tracking_time, now
                end_tracking_time = now
                break
            elif key == ord('q'):
                # If q is pressed, quit
                print "Aborted", done_tracking, start_tracking_time, now
                end_tracking_time = now
                break

            if modality == "tracking":
                cv2.putText(result, "TRACKING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
                cv2.putText(result,
                            "ph: %f, mol: %f mM, generation: %d, ind_num: %d, replica: %d" %
                            (round(ph, 2), round(molarity, 2), gen, individual_num, replica_num),
                            (150, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255))

            if recording:
                out.write(result)
                cv2.putText(result, "RECORDING", (150, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
            counter += 1
        # END WHILE TRUE

        initial_point_s, ending_point_s, droplet_area = track2.show_output_biggest(result)

        point_i = np.float32([initial_point_s[0], initial_point_s[1], 1])
        rob_cor_i = np.dot(self.decanol_syringe.affineMat, point_i)
        initial_point = (rob_cor_i[0].item(), rob_cor_i[1].item())
        print "Coordinates of the initial point of the droplet (mm): " + str(initial_point)

        point_e = np.float32([ending_point_s[0], ending_point_s[1], 1])
        rob_cor_e = np.dot(self.decanol_syringe.affineMat, point_e)
        ending_point = (rob_cor_e[0].item(), rob_cor_e[1].item())
        print "Coordinates of the end point of the droplet (mm): " + str(ending_point)

        print "The droplet area is: " + str(droplet_area)

        print 'the coordinates of the center of the petridish are: ' + str((x, y), )

        edge_check = _calculate_pitagora((x, y), ending_point)
        print 'FUCK THIS SHIT'
        print 'this is the START POINT: ' + str(initial_point)
        print 'this is the edge check: ' + str(edge_check)
        # check if the distance done by the droplet is smaller than the radius of the petridish

        droplet_diameter = math.sqrt(droplet_area / 3.14) * 2.0
        print 'the diameter of the droplet is: ' + str(droplet_diameter)
        radius_mm = 45.0

        limit_edge = radius_mm - (droplet_diameter / 3.11)
        print 'this is the limit edge : ' + str(limit_edge)

        if edge_check < limit_edge:
            # the end point is within the distance
            fitness_value = _calculate_pitagora(initial_point, ending_point) / \
                            (_calculate_pitagora(ending_point, salt_destination) + (2.0 * radius_mm))
            print 'not at border'
        else:
            fitness_value = 0.0
            print 'at border'

        print "the fitness value registered is %f" % fitness_value

        text = "ph: %f, mol: %f mM, generation: %d, individual number: %d, replica: %d, fitness_value: %f" % (
            ph, molarity, gen, individual_num, replica_num, fitness_value)
        track2.add_text_on_screen(result, text)

        if recording:
            import os
            date = str(datetime.datetime.now())
            file_name = os.path.join(FILE_PATH,
                                     "%s_fitness%f.jpg" % (vT.removeColon(date + file_name_addition), fitness_value))
            cv2.imwrite(file_name, result)
            out.release()

        import csv
        with open('/Users/capo/Documents/data_from_exp/paths/' + file_name_addition + "-{}.csv".format(
                start_tracking_time.strftime("%Y-%m-%d %H.%M.%S")), 'wb') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([
                'X salt',
                'Y salt',
                'X droplet Start',
                'Y droplet Start',
                'real_X droplet Start',
                'real_Y droplet Start',
                'X droplet End',
                'Y droplet End',
                'time',
                'fitness',
                'ph',
                'molarity',
                'generation',
                'individual_number',
                'replica'
            ])
            tracking_time = (end_tracking_time - start_tracking_time).total_seconds()

            writer.writerow([
                salt_destination[0],
                salt_destination[1],
                decanol_start[0],
                decanol_start[1],
                initial_point[0],
                initial_point[1],
                ending_point[0],
                ending_point[1],
                tracking_time,
                fitness_value,
                ph,
                molarity,
                gen,
                individual_num,
                replica_num
            ])
        print('----->', decanol_start, ending_point, salt_destination, tracking_time, fitness_value)

        return fitness_value

    def quit(self):
        self.evobot.disconnect()
        self.head.dataLogger.file.close()
        self.decanoate_syringe.dataLogger.file.close()
