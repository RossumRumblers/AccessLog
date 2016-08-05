import time
import evdev
import mainWindow
import sheetReporter
from dependencies import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

#regular expression for identifying ASU Student ID's
IDregex = ";601744(\d{10})1(\d{10})\?"
# hardware ID's for the Scanner
device_IDs = ["5131","2007"]


#
# some code from http://stackoverflow.com/a/33453124
#
class Worker(QObject):
    # create emitters
    finished = pyqtSignal()
    update = pyqtSignal()
    readerDevice = initReader(device_IDs[0], device_IDs[1])

    @pyqtSlot()
    def USBworker(self):
        if not self.readerDevice:
            self.finished.emit()
        self.readerDevice.grab()
        while(True):
            # retrieve data from card scanner
            print("scanning")
            IDdata = interpretEvents(readData(self.readerDevice))
            IDnum = extractID(IDdata, IDregex)
            if not IDnum:
                continue
            #report ID
            sheetReporter.Reporter().log(IDnum)
            #ensure the ID isnt double logged
            IDnum = None

            self.update.emit()
        self.readerDevice.ungrab()
        self.finished.emit()

    def USBworkerfinish(self):
        self.readerDevice.ungrab()