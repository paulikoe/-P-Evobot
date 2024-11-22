import sys

sys.path.append('../api')
sys.path.append('../settings')
from local import *
import cv2
from users.silvia.petri_dish_coordinates import petridishes
from syringe import Syringe
from datalogger import DataLogger
from evobot import EvoBot
from head import Head
from worldcor import WorldCor

usrMsgLogger = DataLogger()
evobot = EvoBot(PORT_NO, usrMsgLogger)
head = Head(evobot)
window_size = (1280, 720)
cap = cv2.VideoCapture(1)

decanol_syringe = Syringe(evobot, SYRINGES['SYRINGE4'])
decanol_syringe.home()

decanol_syr_coord = WorldCor(decanol_syringe, mode='default')

cv2.namedWindow('Window')
cap.set(3, window_size[0])
cap.set(4, window_size[1])

while True:
    ret, frame = cap.read()  # Read a new frame from the camera
    if ret == 0:
        print "ERROR READING INPUT"
    result = frame.copy()
    i = 0
    for petri in petridishes:
        i += 1
        x = petri.center[0]
        y = petri.center[1]
        radius_pix = 132
        # the coordinates need to be transformed in order to be used for the mask
        x_in_pixels = int(decanol_syr_coord.mmTopix((x, y))[0])
        y_in_pixels = int(decanol_syr_coord.mmTopix((x, y))[1])
        # print x_in_pixels
        # print y_in_pixels
        cv2.circle(result, (x_in_pixels, y_in_pixels), radius_pix, (0, 0, 255), 2)
        # cv2.putText(result, "individual: %d, (160, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)

    ph = 8
    molarity = 9
    cv2.putText(result, "TRACKING MODE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, 255)
    cv2.putText(result, "ph: %d, mol: %d" % (ph, molarity), (150, 20), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255))
    cv2.imshow('Window', result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

