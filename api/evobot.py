import sys #Poskytuje přístup k některým proměnným používaným nebo udržovaným interpretem Pythonu.
import time
import threading #Poskytuje podporu pro vlákna ke spouštění úkolů souběžně.
import signal #Poskytuje mechanismy pro používání signálů (např. signál přerušení).
import time
from error_handler import ErrorHandler #Externí modul pro zpracování chyb

from printcore import printcore as PrintCore #Externí modul pro zpracování komunikace s tiskovým jádrem.

_evobot = None


def _evobot_handler(signum, frame):
    if _evobot:
        _evobot.disconnect()
    sys.exit()


class EvoBot:
    """
    This class represents the robot as a whole. It is mainly used to
    initialize the robot.
    """

    def __init__(self, port, _usrMsgLogger=None, error_handler = None):
        """
        This initializes the serial connection to the robot
        and initializes the head. The port argument indicate the
        usb port to which the robot is attached. Typically,
        something of the form "/dev/tty.usbXXXXX". The
        _usrMsgLogger arguments is a function that takes a
        line as input. This method is called everytime
        there is a message relevant to the user.
        """

        global _evobot
        _evobot = self
        signal.signal(signal.SIGINT, _evobot_handler)
        self.printcore = PrintCore()
        self.printcore.recvcb = self._recvcb
        self.usrMsgOutput = _usrMsgLogger
        if not error_handler: 
            self.error_handler = ErrorHandler(self)
        else:
            self.error_handler = error_handler
        self.modules = []
        self.heads = []
        self.populatedSockets = []
        self.event = threading.Event()
        self.connect(port)
        self.iniTime = time.time()  # initial time (cpu clock)
        self.homed_all_axes = False

    def _logUsrMsg(self, line):
        """
        Private method that checks if a user message
        logger has been attached before trying to output
        to it.
        """

        if self.usrMsgOutput is not None:
            try:
                self.usrMsgOutput(line)
            except:
                pass

    def reset(self):
        """
        This resets the robot.
        """
        self.printcore.reset()

    def _recvcb(self, line):
        """
        Private method responsible for passing data from robot to modules (e.g. head, syringe)
        """

        self._logUsrMsg('_recvcb function, line received: ' + str(line)) 
        line = line.decode('utf-8') 
        #self._logUsrMsg('_recvcb function, line received (utf-8): ' + str(line))

        if line.startswith('PS'):
            self.populatedSockets = str(line).split()[1:]
            self.event.set()
        elif line.startswith('HOMED FALSE'):
            self.homed_all_axes = False
            self.event.set()
        elif line.startswith('HOMED TRUE'):
            self.homed_all_axes = True
            self.event.set()
        elif line.startswith('ERROR'):
            self.error_handler._recvcb(line)
        elif line.startswith('Syringe Driver') or line.startswith('Plunger Driver'):
            self._logUsrMsg(line)
        else:
            for head in self.heads:
                if head._recvcb is not None:
                    try:
                        head._recvcb(line)
                    except:
                        pass

            for module in self.modules:
                if module._recvcb is not None:
                    try:
                        module._recvcb(line)
                    except:
                        pass

    def hasHomed(self):
        """
        This method checks if the robot has been homed since last power-on
        """
        self.send('M298')
        self.event.wait()
        self.event.clear()
        return self.homed_all_axes

    def connect(self, port):
        """
        This method must be called before any other commands.
        It creates a connection to the robot over the serial line
        and hones all modules.
        """
        baud = 250000

        self._logUsrMsg('connecting to EvoBot on port %s at baud %s' % (port, baud))
        self.printcore.connect(port, baud)
        self.connected = True
        time.sleep(2)
        self._logUsrMsg('synchronizing head position..')
        self.send('M114')
        time.sleep(0.1)
        self.send('M114')
        time.sleep(0.1)
        self._logUsrMsg('synchronized head position')
        self._logUsrMsg('connected to EvoBot')
        #self.detectPopulatedSockets() to self.detectPopulatedSockets
        self.detectPopulatedSockets()

    def detectPopulatedSockets(self):
        self._logUsrMsg('Detecting populated sockets...')
        self.send('M292')
        self.event.wait()
        self.event.clear()
        self._logUsrMsg('Detected populated sockets: ' + str(self.populatedSockets))

    def home(self):
        """
        This method homes all modules
        """

        self._logUsrMsg('homing all...')
        for module in self.modules:
            module.home()
        for head in self.heads:
            head.home()
        self._logUsrMsg('homed all...')

    def homeHead(self):
        """
        This method homes just the head
        """

        self._logUsrMsg('homing head...')

        for head in self.heads:
            head.home()
        self._logUsrMsg('homed head...')

    def disconnect(self):
        """
        This disconnects the serial communication to the robot.
        """

        self._logUsrMsg('disconnecting...')
        if (self.connected):
            self.printcore.disconnect()
        self.connected = False
        self._logUsrMsg('disconnected')

    def quit(self):
        """
        This disconnects the serial communication with the robot and closes the program
        """
        self.disconnect()
        sys.exit()

    def stop(self):
        """
        This does an emergency stop of the robot.
        """

        self.printcore.send('M112')
        self.connected = False
        self.printcore.disconnect()
        self._logUsrMsg('halted - robot inresponsive until it has been reset')

    def send(self, message):
        """
        This is a debug feature that allows you to send a
        raw g-code command to the robot e.g. "G28" homes the head
        """

        self.printcore.send(message)


'''
Celkově vzato, tato třída slouží k zapouzdření funkcí potřebných pro ovládání robota, včetně komunikace, 
řízení stavu, detekce a zpracování příchozích dat od robota. Je navržena pro ovládání 
a monitorování různých aspektů chodu robota a umožňuje uživateli provádět různé operace, jako je připojení, odpojení, 
domovská pozice a odesílání příkazů G-kódu pro ovládání pohybů robota.

'''