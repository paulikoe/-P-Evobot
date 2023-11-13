import functools
import threading
from threading import Thread
from select import error as SelectError
import time, getopt, sys
from configuration import *

try:
    USE_SIMULATOR
except NameError:
    from physical import robot as Robot
else:
    if USE_SIMULATOR:
        from simulated import robot as Robot
    else:
        from physical import robot as Robot


class printcore():
    def __init__(self, port=None, baud=None):
        """Initializes a printcore instance. Pass the port and baud rate to connect immediately
        """
        self.baud = None
        self.port = None
        self.robot = None
        self.clear = threading.Event()  # clear to send, enabled after responses
        self.lineno = 1
        self.stop_read_thread = True
        self.read_thread = None
        self.tempcb = None  # impl (wholeline)
        self.recvcb = None  # impl (wholeline)
        self.sendcb = None  # impl (wholeline)
        self.errorcb = None  # impl (wholeline)
        self.loud = False  # emit sent and received lines to terminal
        self.greetings = ['start', 'Grbl ']
        if port is not None and baud is not None:
            self.connect(port, baud)

    def disconnect(self):
        """Disconnects from robot
        """
        self.stop_read_thread = True
        if self.read_thread is not None:
            self.read_thread.join()

        if (self.robot):
            self.robot.close()

        self.robot = None

    def connect(self, port=None, baud=None):
        """Set port and baudrate if given, then connect to robot
        """
        if (self.robot):
            self.disconnect()
        if port is not None:
            self.port = port
        if baud is not None:
            self.baud = baud
        self.robot = Robot()
        self.robot.connect(self.port, self.baud)
        self.stop_read_thread = False
        self.read_thread = Thread(target=self._listen)
        self.read_thread.start()

    def reset(self):
        """Reset the robot
        """
        if (self.robot):
            self.robot.reset()

    def _listen(self):
        """This function acts on messages from the firmware
        """
        self.clear.set()
        while (not self.stop_read_thread):
            if (not self.robot or not self.robot.isOpen):
                break
            line = self.robot.readline()

            if line is None:
                continue

            if (len(line) > 1):
                if not line.startswith(b'ok') and self.recvcb is not None:
                    try:
                        self.recvcb(line)
                    except:
                        pass
                if self.loud:
                    print ("RECV: ", line.rstrip())
            #if (line.startswith('Error:Line')):
            if line.startswith(b'Error:Line'):
                terms = line.split()
                self.lineno = int(terms[9]) + 1
            if (line.startswith(b'DEBUG_')):
                continue
            #if (line.startswith(tuple(self.greetings)) or line.startswith(b'ok')):
            if line.startswith(tuple(greeting.encode() for greeting in self.greetings)) or line.startswith(b'ok'):

                self.clear.set()
            #if (line.startswith(tuple(self.greetings)) or line.startswith(b'ok') or "T:" in line):
            if (line.startswith(tuple(greeting.encode() for greeting in self.greetings)) or line.startswith(b'ok') or b'T:' in line):

                if (line.startswith(b'ok')):
                    # put temp handling here
                    if b"T:" in line and self.tempcb is not None:
                        try:
                            self.tempcb(line)
                        except:
                            pass
                            # callback for temp, status, whatever
            elif (line.startswith(b'Error')):
                if self.errorcb is not None:
                    try:
                        self.errorcb(line)
                    except:
                        pass
                        # callback for errors
            if line.startswith(b'Error:Printer halted. kill() called!'):
                self.stop_read_thread = True
            #if line.lower().startswith("resend") or line.startswith("rs"):
            if line.lower().startswith(b"resend") or line.startswith(b"rs"):

                self.clear.set()

    def _checksum(self, command):
        return functools.reduce(lambda x, y: x ^ y, map(ord, command))

    def send(self, command):
        """ calc checksum and send command immediately
        """

        self.clear.wait()
        self.clear.clear()
        self._send(command, self.lineno, True)
        self.lineno += 1

    def _send(self, command, lineno=0, calcchecksum=False):
        if (calcchecksum):
            prefix = "N" + str(lineno) + " " + command
            command = prefix + "*" + str(self._checksum(prefix))
        if (self.robot):
            if self.loud:
                print ("SENT: ", command)
            if self.sendcb is not None:
                try:
                    self.sendcb(command)
                except:
                    pass
            self.robot.write(str(command + "\n"))
