from PyQt5.QtWidgets import QMainWindow
from MainWindow import Ui_MainWindow


#import printcore
#from time import sleep

def absorbliquid(iniX, iniY, vol):
    
    
    global location
    
    if 0 <vol<30 and 0 <iniX<210 and 0 <iniY<340:
        
        
        absorbini = 'G1 X%f Z%f' % (iniX, iniY)
        r=.0230329
        #h=round(number[, 1])
        h= vol / (3.1415 *r*r*1000)
        syringedown = 'M290 S-20'
        location = 20-h
        plungerup = 'M290 P%f' % (location,)
        syringeup = 'M290 S0'
        gcode = ['G290 P20', 'G4 P500',syringedown, 'G4 P500', absorbini, 'G4 P500', plungerup, 'G4 P500', syringeup]
        
        """gcode = ['M43 P4 S10', 'G4 P500', 'G1 F9000', 'G4 P500']
        gcode +=  [iniGrip, 'M43 P4 S40', 'G4 P500','M43 P4 S45', 'G4 P500','M43 P4 S50', 'G4 P500','M43 P4 S55', 'G4 P500','M43 P4 S60', 'G4 P500']
        gcode += ['M43 P4 S65', 'G4 P500','M43 P4 S70', 'G4 P500',endGrip, 'M43 P4 S65', 'G4 P500','M43 P4 S60', 'G4 P500','M43 P4 S55', 'G4 P500']
        gcode += ['M43 P4 S50', 'G4 P500','M43 P4 S45', 'G4 P500','M43 P4 S40', 'G4 P500','M43 P4 S10']"""
        return gcode
        print (iniX, iniY, vol)
        
        
    else:
        print ("Inappropriate Dimension argument 1")
    
    

def putliquid(destX, destY, Dvol):
    
    r=.0230329
    hprime= Dvol / (3.1415 *r*r*1000)
    Dh=location+hprime
    
    
    if 0 < Dh <= 20 and 0 <destX<210 and 0 <destY<340:
        putdest = 'G1 X%f Z%f' % (destX, destY)
        
        
        Dsyringedown = 'M290 S-20'
        Dplungerdown = 'M290 P%f' % (Dh,)
        Dsyringeup = 'M290 S0'
        
        
        gcode = [putdest, 'G4 P500', Dsyringedown, 'G4 P500', Dplungerdown, 'G4 P500', Dsyringeup]
        return gcode
    
    else:
        print ("Inappropriate Dimension argument 2"), location, Dh, destX, destY
        

#p = printcore.printcore("/dev/tty.usbmodem1411",250000)
#p.loud=True
#sleep(3)


#gcode= ['M290 S-20']
#gcode= ['M291','G4 P500','G28']

#gcode += absorbliquid(100,150,20) + putliquid(200,200,5) 
#gcode += absorbliquid(5,6,10,) + putliquid(10,10,5)
#gcode += absorbliquid(5,6,10,) + putliquid(10,10,5)


#print gcode
#p.startprint(gcode)
#sleep(3)
















class Application(QMainWindow):

    def __init__(self):
        super(Application, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.buttonClose.clicked.connect(self.__CloseWindow)
        self.ui.buttonWrite.clicked.connect(self.__WriteName)
        
        self.ui.sendButton.clicked.connect(self.__SendCommand)

    def __CloseWindow(self):
        self.close()

    def __WriteName(self):
        strName = self.ui.lineName.text()
        self.ui.labelResult.setText("Your name is " + strName)


    def __SendCommand(self):
        iniX = int(self.ui.lineEditgx.text())
        iniY = int(self.ui.lineEditgy.text())
        vol = float(self.ui.lineEditgvolume.text())
        #vol=unicodedata.numeric(u %strvol)
        destX = int(self.ui.lineEditdx.text())
        destY = int(self.ui.lineEditdy.text())
        Dvol = float(self.ui.lineEditdvolume.text())
        #Dvol=unicodedata.numeric(u %strDvol)
        
        gcode= ['M291','G4 P500','G28']
        gcode += absorbliquid(iniX, iniY, vol) + putliquid(destX, destY, Dvol) 
        self.ui.label_gcoderesult.setText("Your code is : " + str(gcode)) 
