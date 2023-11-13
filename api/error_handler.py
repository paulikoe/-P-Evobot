class ErrorHandler:
    """This class handles error messages received from the robot
    It should throw different kinds of exceptions depending
    on which kind of error message is received from the robot
    """

    def __init__(self, evobot):
        self.evobot = evobot

    def _recvcb(self, line):
        """
        Private method responsible for parsing error message and deciding
        which kind of exception should be thrown
        """    
        if line.startswith( 'ERROR' ):
            print ("Received error: " + str(line))
