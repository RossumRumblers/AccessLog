#!/usr/bin/python3
'''
Main GUI file

Version 2.2.1B
'''

import sys
import worker
import mainWindow
import sheetReporter

from dependencies import miscFunc
from JSONReader import JSONReader
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QRadioButton, QMessageBox


class Form(QMainWindow, mainWindow.Ui_MainWindow):
    '''
    Main Gui Form Class
    '''

    def __init__(self):
        if not miscFunc.testRoot():
            print("Please rerun this script with root.")
            sys.exit()
        if not miscFunc.testInternet():
            print("Please Verify this machine is connected to the internet.")
            sys.exit()
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.postSetup()
        sheetReporter.Reporter() # init Google API

        #
        # worker thread code from http://stackoverflow.com/a/33453124
        #
        self.workerobj = worker.Worker(self)                    # instatiate worker object
        self.wThread = QThread()                                # instatiate worker thread

        self.workerobj.moveToThread(self.wThread)               # move the worker object into the worker thread

        #emitters enable inter-thread function calls
        self.workerobj.updateStatus.connect(self.updateStatus)  # connect the updateStatus emitter to the updateStatus function
        self.workerobj.Alert.connect(self.Alert)                # do the same for alert

        self.wThread.started.connect(self.workerobj.USBworker)  # on thread started: run the USBworker function
        self.wThread.start()                                    # start the worker thread

        #attach button/keyboard key listeners
        self.lineEdit.returnPressed.connect(self.pushButton.click)
        self.pushButton.clicked.connect(self.buttonPushed)

        #show the window
        self.show()
        self.Alert('indkfjgnfo', 'test')


    def postSetup(self):
        '''
        Function to be executed after window creation
        '''

        #Comment out this line to give the window a frame (and thus, a close button)
        #self.setWindowFlags(Qt.FramelessWindowHint)
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        frameGeo = self.frameGeometry()
        frameGeo.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frameGeo.topLeft())
        # attempt to center the window on screen

        i = 0
        for radio in self.findChildren(QRadioButton):
            #dynamically populate club radio-button list
            try:
                elem = JSONReader().getClubNameLong(JSONReader().getClubList()[i])
                radio.setText(elem)
            except IndexError:
                radio.hide()
            i += 1

    def W_onFinished(self):
        '''
        Worker thread cleanup function
        '''
        self.wThread.quit()
        self.obj.USBworkerfinish()

    def buttonPushed(self):
        '''
        Function to execute when the submit button or return key is pushed
        '''

        IDnum = self.lineEdit.text()
        if IDnum == "":
            self.updateStatus("Please Enter an ASU ID", 3)
        else:
            self.updateStatus("Logging...", 0)
            self.lineEdit.setText("")
            if len(IDnum) == 10 and IDnum.isdigit():
                clubName = self.getSelectedRadio()
                self.setSelectedRadio(clubName)
                clubID = None
                for club in JSONReader().getClubList():
                    if JSONReader().getClubNameLong(club) == clubName:
                        clubID = club
                self.updateStatus(sheetReporter.Reporter().log(IDnum, clubID), 3)
            else:
                self.updateStatus("Please Enter an ASU ID", 3)

    def getSelectedRadio(self):
        '''get Selected Radio Button'''
        for radio in self.findChildren(QRadioButton):
            if radio.isChecked():
                return radio.text()

    def setSelectedRadio(self, name):
        '''set Selected Radio Button'''
        for radio in self.findChildren(QRadioButton):
            if name == radio.text():
                radio.setChecked(True)

    def Alert(self, mb_type, mb_message):
        '''Opens messageBox

        type is 'info', 'warn', or 'crit'
        '''
        if mb_type == 'info':
            # Information
            QMessageBox.information(self, 'Information', mb_message).exec()
        elif mb_type == 'warn':
            # Warning
            QMessageBox.warning(self, 'Warning', mb_message).exec()
        elif mb_type == 'crit':
            # Critical
            QMessageBox.critical(self, 'Severe Error', mb_message).exec()
        else:
            # Error throwing Error. Oh God...
            QMessageBox.critical(self, 'Error', 'Error displaying Error.\nNow is the time to panic.').exec()

    def updateStatus(self, message, time):
        '''
        Update the status bar in the window

        time is in seconds
        '''
        self.statusBar.showMessage(message, time*1000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Form()
    app.exec_()
    sys.exit()
