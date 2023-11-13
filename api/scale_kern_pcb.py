# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import serial
import time

_PORT = 'COM31'
_BAUDRATE = 19200


class Scale:
    def __init__(self, port):
        global ser
        _PORT = port
        ser = serial.Serial(_PORT, _BAUDRATE, timeout=0.1)  # open serial port

    def _str2float(self, str):
        """
        This function transform the ASCII characters form the scale to a float
        """
        s = str[1:12]
        return float(s.replace(" ", ""))

    def tare(self):
        """
        This function tares the scale
        """
        ser.write(b't')  # write a string
        time.sleep(6)
        print "taring"

    def weigh(self):
        """
        This method sends a weigh command and returns the measurement, even if
        the measurement is not stable.
        """
        print "weighting"
        ser.write(b'w')  # write a string
        ser.flush()
        data = ser.readline()
        return self._str2float(data)

    def stableWeigh(self):
        """
        This method reurns a sable weight. It continues sending 
        stable weigh commands until it receives an answer from the scale.
        """
        data = ""
        while not data:
            ser.write(b's')  # write a string
            ser.flush()
            time.sleep(0.5)
            data = ser.readline()
            print data
        return self._str2float(data)

    def quit(self):
        ser.close()  # close port
