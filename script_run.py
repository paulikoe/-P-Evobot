from taking_photos import camera
from run_yolov5 import run_yolov5_detection
from taking_photos import delete_photo
from QReader import process_file
from coordinates_qr import coordinates
from choose import chooseF
'''
Turn on the camera
    - A photo will be taken
'''
#camera()

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
#delete_photo()

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
Selecting the task
'''
chooseF()