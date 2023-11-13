import time
import sys
from serial import Serial, SerialException, PARITY_ODD, PARITY_NONE
import serial.tools.list_ports
import serial
import glob


def serial_ports():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class robot:
    def isOpen():
        return (self.serial.isOpen())

    def __init__(self):
        self.serial = None

    def close(self):
        if self.serial is not None:
            self.serial.close()
            self.serial = None

    def _handleError(self, e):
        if self.serial is not None and self.serial.isOpen():
            print ("connection lost: %s" % e)

    def connect(self, port, baud):
        if self.serial is None or self.serial.isOpen() is False:
            try:
                self.serial = Serial(port=port,
                                     baudrate=baud,
                                     timeout=0.25,
                                     parity=PARITY_ODD)
                self.serial.close()
                self.serial.parity = PARITY_NONE
                self.serial.open()
            except Exception as e:
                self.serial = None
                print ('ERROR: No robot detected on port ' + port)
                availablePorts = serial_ports()
                print ('Available ports:')
                for port in availablePorts:
                    print (port)
                #sys.exit()
                raise Exception('Connection error!')

    def reset(self):
        if self.serial is None and self.serial.isOpen() is True:
            self.serial.setDTR(1)
            time.sleep(0.2)
            self.serial.setDTR(0)

    def readline(self):
        line = None
        if self.serial is not None and self.serial.isOpen() is True:
            try:
                line = self.serial.readline()
            except SerialException as e:
                self._handleError(e)
        return line

    def write(self, string):
        if self.serial is not None and self.serial.isOpen() is True:
            try:
                self.serial.write(string)
            except SerialException as e:
                self._handleError(e)
