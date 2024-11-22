""" LOCAL Configuration file. CREATE A COPY OF THIS FILE AND NAME IT local.py
    Add your local configuration here.

"""

# For MAC. The numbers at the end could change.
PORT_NO = "/dev/tty.usbmodem14121"
# For Windows COMX, where X is the number of the port.
# PORT_NO = "COM5"

CAMERA_ID = 0
# ID is the slot the syringe is on, GOAL_POS is how much the syringe should go down to reach its goal. e.g. droplet
# i.e syringe1 is on slot 9, and should go down 30 mm
SYRINGES = {
    'SYRINGE0': {'ID': 16, 'SYRINGE_LIMIT': -69, 'PLUNGER_LIMIT': 50, 'GOAL_POS': -45, 'PLUNGER_CONVERSION_FACTOR': 1},
    'SYRINGE1': {'ID': 9, 'SYRINGE_LIMIT': -68, 'PLUNGER_LIMIT': 50, 'GOAL_POS': -55, 'PLUNGER_CONVERSION_FACTOR': 1}, #38
    'SYRINGE2': {'ID': 13, 'SYRINGE_LIMIT': -47, 'PLUNGER_LIMIT': 42, 'GOAL_POS': -30, 'PLUNGER_CONVERSION_FACTOR': 1},
    'SYRINGE3': {'ID': 14, 'SYRINGE_LIMIT': -70, 'PLUNGER_LIMIT': 50, 'GOAL_POS': -24, 'PLUNGER_CONVERSION_FACTOR': 1}
}


PUMPS = {
    'PUMP1': {'PUMP_SOCKET': 'E0', 'PUMP_CONVERSION_FACTOR': 1},
    'PUMP2': {'PUMP_SOCKET': 'Y', 'PUMP_CONVERSION_FACTOR': 1},
    'PUMP3': {'PUMP_SOCKET': 'E1', 'PUMP_CONVERSION_FACTOR': 1}
}

# ID is the slot where the scanner is on. 
# i.e scanner1 is on slot 6, and it can go down 65 mm
SCANNERS = {
    'SCANNER1': {'ID': 6, 'SCANNER_LIMIT': 65}
}

FILE_PATH = "/Users/capo/Documents/data_from_exp"
EVOBLISS_SOFTWARE_PATH = "/Users/capo/evobliss-software"

USE_SIMULATOR = False
