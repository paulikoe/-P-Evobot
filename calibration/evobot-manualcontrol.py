# -*- coding: utf-8 -*-
import sys
import time
import functools
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget

sys.path.append('../api')
sys.path.append('../settings')
from configuration import *
from evobot import EvoBot
from datalogger import DataLogger
from syringe import Syringe
from head import Head

class Example(QWidget):
    def __init__(self):
        super(Example,self).__init__()
        self.interfaceActive = False
        usrMsgLogger = self.updateTextBox
        self.evobot = EvoBot("COM5", usrMsgLogger)
        self.head = Head( self.evobot )
        self.syringes = []
        self.syringeEdits = []
        self.plungerEdits = []        
        for i in self.evobot.populatedSockets:
            for j in SYRINGES:
                if int(SYRINGES[j]['ID'])==int(i):
                    self.syringes.append( Syringe( self.evobot, SYRINGES[j] ) )

        self.initUI()
        self.interfaceActive = True
        self.updateTextBox( "init completed" )

    def quit(self):
        self.interfaceActive = False
        self.evobot.disconnect( )
        QtCore.QCoreApplication.instance().quit()
        sys.exit()
        
    def closeEvent(self, event):
        self.quit()
        event.accept()

    def stop(self):
        self.interfaceActive = False
        self.evobot.stop()
        QtCore.QCoreApplication.instance().quit()
        sys.exit()
        
    def updateTextBox( self, line ):
        if self.interfaceActive == True:
            self.headXTitleEdit.setText( str( self.head.getX() ) )
            self.headYTitleEdit.setText( str( self.head.getY() ) )
            for idx, val in enumerate(self.syringeEdits):
                val.setText(  str( self.syringes[idx].syringeGetPos() ) )
            for idx, val in enumerate(self.plungerEdits):                
                val.setText( str( self.syringes[idx].plungerGetPos() ) )
            self.consoleTextEdit.append(line)
            self.update()
        else:
            print(line)
        
    def home(self):
        self.evobot.home()
                        
    def headMove(self):
        x = float(self.headXTitleEdit.text())
        y = float(self.headYTitleEdit.text())
        self.head.move( x,y )

    def executeCommand(self):
        self.evobot.send( self.commandEdit.text() )
        
    def syringeMove( self, currentSyringe ):
        for idx, syringe in enumerate(self.syringes):
            if syringe.syringeID == currentSyringe:
                sMove = float( self.syringeEdits[idx].text() )
                syringe.syringeMove( sMove )
                self.syringeEdits[idx].setText(  str( syringe.syringeGetPos() ) )
                self.syringeEdits[idx].update()
        
    def plungerMove( self, currentSyringe ):
        for idx, syringe in enumerate(self.syringes):
            if syringe.syringeID == currentSyringe:
                pMove = float( self.plungerEdits[idx].text() )
                syringe.plungerMovePos( pMove )
                self.plungerEdits[idx].setText(  str( syringe.plungerGetPos() ) )
                self.plungerEdits[idx].update()
        
    def initUI(self):        
        gridTopRow = QtWidgets.QGridLayout()
        gridTopRow.setSpacing(10)
        
        btnHome = QtWidgets.QPushButton('Home', self)
        btnHome.setToolTip('Homes the EvoBot head')
        btnHome.clicked.connect(self.home )
        btnHome.resize(btnHome.sizeHint())
        gridTopRow.addWidget(btnHome, 0, 1)
        
        btnQuit = QtWidgets.QPushButton('Quit', self)
        btnQuit.setToolTip('Quits program')
        btnQuit.clicked.connect(self.quit)
        btnQuit.resize(btnQuit.sizeHint())
        gridTopRow.addWidget(btnQuit, 0, 2)

        btnStop = QtWidgets.QPushButton('STOP!', self)
        btnStop.setToolTip('Emergency stop')
        btnStop.clicked.connect(self.stop)
        btnStop.resize(btnStop.sizeHint())
        gridTopRow.addWidget(btnStop, 0, 3)

        headXTitle = QtWidgets.QLabel('Head X,Y Position')
        self.headXTitleEdit = QtWidgets.QLineEdit()
        self.headXTitleEdit.setText( 'Unknown until homed' )
        self.headYTitleEdit = QtWidgets.QLineEdit()
        self.headYTitleEdit.setText( 'Unknown until homed' )
        gridTopRow.addWidget(headXTitle, 1, 0)
        gridTopRow.addWidget(self.headXTitleEdit, 1, 1)
        gridTopRow.addWidget(self.headYTitleEdit, 1, 2)

        btnHeadMove = QtWidgets.QPushButton('Move', self)
        btnHeadMove.setToolTip('Move head')
        btnHeadMove.clicked.connect(self.headMove)
        btnHeadMove.resize(btnHeadMove.sizeHint())
        gridTopRow.addWidget(btnHeadMove, 1, 3)

        btnHeadMove = QtWidgets.QPushButton('Move', self)
        btnHeadMove.setToolTip('Move head')
        btnHeadMove.clicked.connect(self.headMove)
        btnHeadMove.resize(btnHeadMove.sizeHint())
        gridTopRow.addWidget(btnHeadMove, 1, 3)

        headSyringeTitle1 = QtWidgets.QLabel('No.')
        headSyringeTitle2 = QtWidgets.QLabel('Syringe')
        headSyringeTitle3 = QtWidgets.QLabel('Plunger')

        gridTopRow.addWidget(headSyringeTitle1, 2, 0)
        gridTopRow.addWidget(headSyringeTitle2, 2, 1)
        gridTopRow.addWidget(headSyringeTitle3, 2, 2)

        currentRow = 3
        for syringe in self.syringes:
            syringeTitle = QtWidgets.QLabel( str( syringe.syringeID ))
            syringeEdit = QtWidgets.QLineEdit()
            syringeEdit.setText( 'unknown' )
            self.syringeEdits.append( syringeEdit )
            plungerEdit = QtWidgets.QLineEdit()
            plungerEdit.setText( '0' )
            self.plungerEdits.append( plungerEdit )

            btnSyringeMove = QtWidgets.QPushButton('Move', self)
            btnSyringeMove.setToolTip('Move syringe ' + str( syringe.syringeID ) )
            btnSyringeMove.clicked.connect( functools.partial( self.syringeMove, syringe.syringeID)  )
            btnSyringeMove.resize(btnSyringeMove.sizeHint())

            btnPlungerMove = QtWidgets.QPushButton('Plunge!', self)
            btnPlungerMove.setToolTip('Move plunger ' + str( syringe.syringeID ) )
            btnPlungerMove.clicked.connect( functools.partial( self.plungerMove, syringe.syringeID)  )
            btnPlungerMove.resize(btnPlungerMove.sizeHint())

            gridTopRow.addWidget(syringeTitle, currentRow, 0)
            gridTopRow.addWidget(syringeEdit, currentRow, 1)
            gridTopRow.addWidget(plungerEdit, currentRow, 2)
            gridTopRow.addWidget(btnSyringeMove, currentRow + 1, 1)
            gridTopRow.addWidget(btnPlungerMove, currentRow + 1, 2)
            currentRow = currentRow + 2

        commandTitle = QtWidgets.QLabel('Command')
        self.commandEdit = QtWidgets.QLineEdit()
        btnCommand = QtWidgets.QPushButton('Execute', self)
        btnCommand.clicked.connect(self.executeCommand)

        gridTopRow.addWidget(commandTitle, currentRow, 0)
        gridTopRow.addWidget(self.commandEdit, currentRow, 1, 1, 2)
        gridTopRow.addWidget(btnCommand, currentRow, 3)
        currentRow = currentRow + 1

        consoleTitle = QtWidgets.QLabel('EvoBot Output')
        gridTopRow.addWidget(consoleTitle, currentRow, 0)
        currentRow = currentRow + 1

        self.consoleTextEdit = QtWidgets.QTextEdit()
        self.consoleTextEdit.setReadOnly( True )
        gridTopRow.addWidget(self.consoleTextEdit, currentRow, 0, currentRow + 6, 4)
        currentRow = currentRow + 7        

        self.setLayout(gridTopRow)                    

        self.resize(self.sizeHint())
        self.setWindowTitle('EvoBot Manual Control Station')    
        self.show()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    app.exec_()
