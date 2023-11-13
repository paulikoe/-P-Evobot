import time
import threading
import datetime


class VoltageSensor:
    def __init__(self, _evobot, _id):
        """
        This method initialize the voltage sensor. The parameters
        are the evobot object to which this syringe is attached and the ID of
        the voltage channel to measure.
        """
        self.evobot = _evobot
        self.evobot.modules.append(self)
        self.sensorID = _id
        self.dataLogger = None
        self.voltage = None
        self.newMeasurementAvailable = threading.Event()

    def _recvcb(self, line):
        """
        Private methods that handles messages received from the robot
        """

        terms = []
        if line.startswith('V '):
            terms = str(line).split()
            if (self.sensorID == int(terms[1])):
                self.voltage = float(terms[3])
                if self.dataLogger is not None:
                    try:
                        current_time = datetime.datetime.now().time()
                        self.dataLogger(str(current_time.isoformat()) + ' ' + str(self.voltage) + "\n")
                    except:
                        pass
                self.newMeasurementAvailable.set()

    def setDataLogger(self, logger):
        """
        This sets the data logger for the voltage sesnor. The data logged consist
        of the time and voltage. The argument
        is a function that takes a string as input.
        """

        self.dataLogger = logger

    def getMeasurement(self):  # Volts
        """
        This returns the voltage in Volts.
        """

        self.evobot._logUsrMsg('Getting voltage measurement')

        sensorMsg = 'M285 V' + str(self.sensorID)
        self.evobot.send(sensorMsg)
        self.newMeasurementAvailable.wait()
        self.newMeasurementAvailable.clear()
        self.evobot._logUsrMsg('Current voltage ' + str(self.voltage) + 'V')
        return (self.voltage)

    def home(self):
        """
        This resets the voltageSensors, currently no actions are taken
        """

    def park(self):
        """
        This resets the voltageSensors, currently no actions are taken
        """
