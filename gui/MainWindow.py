# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Wed Oct 15 11:06:47 2014
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(878, 507)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.buttonWrite = QtWidgets.QPushButton(self.centralwidget)
        self.buttonWrite.setGeometry(QtCore.QRect(440, 410, 114, 32))
        self.buttonWrite.setObjectName("buttonWrite")
        self.buttonClose = QtWidgets.QPushButton(self.centralwidget)
        self.buttonClose.setGeometry(QtCore.QRect(610, 410, 114, 32))
        self.buttonClose.setObjectName("buttonClose")
        self.lineName = QtWidgets.QLineEdit(self.centralwidget)
        self.lineName.setGeometry(QtCore.QRect(130, 370, 591, 21))
        self.lineName.setText("")
        self.lineName.setObjectName("lineName")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(40, 370, 62, 16))
        self.label.setObjectName("label")
        self.labelResult = QtWidgets.QLabel(self.centralwidget)
        self.labelResult.setGeometry(QtCore.QRect(30, 380, 641, 20))
        self.labelResult.setObjectName("labelResult")
        self.connectButton = QtWidgets.QPushButton(self.centralwidget)
        self.connectButton.setGeometry(QtCore.QRect(210, 0, 114, 32))
        self.connectButton.setObjectName("connectButton")
        self.resetButton = QtWidgets.QPushButton(self.centralwidget)
        self.resetButton.setGeometry(QtCore.QRect(320, 0, 114, 32))
        self.resetButton.setObjectName("resetButton")
        self.experimentBox = QtWidgets.QComboBox(self.centralwidget)
        self.experimentBox.setGeometry(QtCore.QRect(50, 50, 171, 21))
        self.experimentBox.setObjectName("experimentBox")
        self.experimentBox.addItem("")
        self.experimentBox.addItem("")
        self.experimentBox.addItem("")
        self.experimentBox.addItem("")
        self.experimentBox.addItem("")
        self.label_grab = QtWidgets.QLabel(self.centralwidget)
        self.label_grab.setGeometry(QtCore.QRect(10, 120, 91, 16))
        self.label_grab.setObjectName("label_grab")
        self.label_gx = QtWidgets.QLabel(self.centralwidget)
        self.label_gx.setGeometry(QtCore.QRect(100, 100, 31, 16))
        self.label_gx.setObjectName("label_gx")
        self.label_gy = QtWidgets.QLabel(self.centralwidget)
        self.label_gy.setGeometry(QtCore.QRect(100, 120, 31, 16))
        self.label_gy.setObjectName("label_gy")
        self.label_gvolume = QtWidgets.QLabel(self.centralwidget)
        self.label_gvolume.setGeometry(QtCore.QRect(90, 140, 62, 16))
        self.label_gvolume.setObjectName("label_gvolume")
        self.lineEditgx = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditgx.setGeometry(QtCore.QRect(150, 100, 113, 21))
        self.lineEditgx.setObjectName("lineEditgx")
        self.lineEditgy = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditgy.setGeometry(QtCore.QRect(150, 120, 113, 21))
        self.lineEditgy.setObjectName("lineEditgy")
        self.lineEditgvolume = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditgvolume.setGeometry(QtCore.QRect(150, 140, 113, 21))
        self.lineEditgvolume.setObjectName("lineEditgvolume")
        self.label_move = QtWidgets.QLabel(self.centralwidget)
        self.label_move.setGeometry(QtCore.QRect(300, 120, 62, 16))
        self.label_move.setObjectName("label_move")
        self.lineEditmx = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditmx.setGeometry(QtCore.QRect(380, 110, 113, 21))
        self.lineEditmx.setObjectName("lineEditmx")
        self.lineEditmy = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditmy.setGeometry(QtCore.QRect(380, 130, 113, 21))
        self.lineEditmy.setObjectName("lineEditmy")
        self.label_dispense = QtWidgets.QLabel(self.centralwidget)
        self.label_dispense.setGeometry(QtCore.QRect(520, 120, 111, 16))
        self.label_dispense.setObjectName("label_dispense")
        self.lineEditdvolume = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditdvolume.setGeometry(QtCore.QRect(690, 140, 113, 21))
        self.lineEditdvolume.setObjectName("lineEditdvolume")
        self.lineEditdx = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditdx.setGeometry(QtCore.QRect(690, 100, 113, 21))
        self.lineEditdx.setObjectName("lineEditdx")
        self.label_dy = QtWidgets.QLabel(self.centralwidget)
        self.label_dy.setGeometry(QtCore.QRect(650, 120, 31, 16))
        self.label_dy.setObjectName("label_dy")
        self.label_dx = QtWidgets.QLabel(self.centralwidget)
        self.label_dx.setGeometry(QtCore.QRect(650, 100, 31, 16))
        self.label_dx.setObjectName("label_dx")
        self.lineEditdy = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditdy.setGeometry(QtCore.QRect(690, 120, 113, 21))
        self.lineEditdy.setObjectName("lineEditdy")
        self.label_dvolume = QtWidgets.QLabel(self.centralwidget)
        self.label_dvolume.setGeometry(QtCore.QRect(640, 140, 62, 16))
        self.label_dvolume.setObjectName("label_dvolume")
        self.sendButton = QtWidgets.QPushButton(self.centralwidget)
        self.sendButton.setGeometry(QtCore.QRect(130, 180, 114, 32))
        self.sendButton.setObjectName("sendButton")
        self.label_gcode = QtWidgets.QLabel(self.centralwidget)
        self.label_gcode.setGeometry(QtCore.QRect(20, 230, 62, 16))
        self.label_gcode.setObjectName("label_gcode")
        self.label_gcoderesult = QtWidgets.QLabel(self.centralwidget)
        self.label_gcoderesult.setGeometry(QtCore.QRect(140, 230, 711, 91))
        self.label_gcoderesult.setText("")
        self.label_gcoderesult.setObjectName("label_gcoderesult")
        self.disconnectButton = QtWidgets.QPushButton(self.centralwidget)
        self.disconnectButton.setGeometry(QtCore.QRect(440, 0, 114, 32))
        self.disconnectButton.setObjectName("disconnectButton")
        self.emergencyButton = QtWidgets.QPushButton(self.centralwidget)
        self.emergencyButton.setGeometry(QtCore.QRect(30, 310, 171, 32))
        self.emergencyButton.setStyleSheet("background-color: rgb(255, 23, 37);")
        self.emergencyButton.setDefault(False)
        self.emergencyButton.setObjectName("emergencyButton")
        self.assembleButton = QtWidgets.QPushButton(self.centralwidget)
        self.assembleButton.setGeometry(QtCore.QRect(310, 310, 161, 32))
        self.assembleButton.setObjectName("assembleButton")
        self.destroyButton = QtWidgets.QPushButton(self.centralwidget)
        self.destroyButton.setGeometry(QtCore.QRect(500, 310, 171, 32))
        self.destroyButton.setObjectName("destroyButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 878, 22))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Open = QtWidgets.QMenu(self.menu_File)
        self.menu_Open.setObjectName("menu_Open")
        self.menu_About = QtWidgets.QMenu(self.menubar)
        self.menu_About.setObjectName("menu_About")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_Image = QtWidgets.QAction(MainWindow)
        self.action_Image.setObjectName("action_Image")
        self.action_Video = QtWidgets.QAction(MainWindow)
        self.action_Video.setObjectName("action_Video")
        self.action_Settings = QtWidgets.QAction(MainWindow)
        self.action_Settings.setObjectName("action_Settings")
        self.actionE_xit = QtWidgets.QAction(MainWindow)
        self.actionE_xit.setObjectName("actionE_xit")
        self.action_Etc = QtWidgets.QAction(MainWindow)
        self.action_Etc.setObjectName("action_Etc")
        self.menu_Open.addAction(self.action_Image)
        self.menu_Open.addAction(self.action_Video)
        self.menu_File.addAction(self.menu_Open.menuAction())
        self.menu_File.addAction(self.action_Settings)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionE_xit)
        self.menu_About.addAction(self.action_Etc)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_About.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.buttonWrite.setText(_translate("MainWindow", "&Write"))
        self.buttonClose.setText(_translate("MainWindow", "&Close"))
        self.connectButton.setText(_translate("MainWindow", "Connect"))
        self.resetButton.setText(_translate("MainWindow", "Reset"))
        self.experimentBox.setItemText(0, _translate("MainWindow", "Martin\'s Experiments"))
        self.experimentBox.setItemText(1, _translate("MainWindow", "Lee\'s Experiments"))
        self.experimentBox.setItemText(2, _translate("MainWindow", "Ioanniss\' Experiments"))
        self.experimentBox.setItemText(3, _translate("MainWindow", "harold\'s Experiments"))
        self.experimentBox.setItemText(4, _translate("MainWindow", "Customized"))
        self.label_grab.setText(_translate("MainWindow", "Grab Liquid"))
        self.label_gx.setText(_translate("MainWindow", "X"))
        self.label_gy.setText(_translate("MainWindow", "Y"))
        self.label_gvolume.setText(_translate("MainWindow", "Volume"))
        self.label_move.setText(_translate("MainWindow", "Move to"))
        self.label_dispense.setText(_translate("MainWindow", "Dispense Liquid"))
        self.label_dy.setText(_translate("MainWindow", "Y"))
        self.label_dx.setText(_translate("MainWindow", "X"))
        self.label_dvolume.setText(_translate("MainWindow", "Volume"))
        self.sendButton.setText(_translate("MainWindow", "Send"))
        self.label_gcode.setText(_translate("MainWindow", "Gcode"))
        self.disconnectButton.setText(_translate("MainWindow", "Disconnect"))
        self.emergencyButton.setText(_translate("MainWindow", "Emergency Stop"))
        self.assembleButton.setText(_translate("MainWindow", "Assemble Robot?"))
        self.destroyButton.setText(_translate("MainWindow", "Destroy Robot"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Open.setTitle(_translate("MainWindow", "&Open"))
        self.menu_About.setTitle(_translate("MainWindow", "&About"))
        self.action_Image.setText(_translate("MainWindow", "&Image"))
        self.action_Video.setText(_translate("MainWindow", "&Video"))
        self.action_Settings.setText(_translate("MainWindow", "&Settings"))
        self.actionE_xit.setText(_translate("MainWindow", "E&xit"))
        self.action_Etc.setText(_translate("MainWindow", "&Etc.."))

