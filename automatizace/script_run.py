import os
from time import sleep
from taking_photos import camera
from run_yolov5 import run_yolov5_detection
from QReader import process_file
from coordinates_qr import coordinates
from choose import choose_assignment
from assignment1 import assignment_1
os.chdir("C:/Python/afaina-evobliss-software-68090c0edb16/automatizace/")
#print("Program is running")

'''
Turn on the camera
    - A photo will be taken
'''

#camera() 
#sleep(5)
#program1.home()
'''
Detection - yolov5
    - QR code detection using neural network weights 
    - obtaining QR code coordinates
'''

run_yolov5_detection()

'''
Delete picture
    - is not necessary, it will overwrite itself
'''
##delete_photo()

'''
Qr detector
    - retrieving the photo and coordinates of the QR 
    codes and adding the text they contain
'''
process_file()

'''
Coordinate conversion
    - Existing coordinates are converted to real world
    coordinates and qr code texts are added
'''
coordinates()

'''
Selecting the task - nemusí, nesmí
'''
#choose_assignment()


