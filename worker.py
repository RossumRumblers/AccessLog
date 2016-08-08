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
    update = pyqtSignal(str,int)
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
            self.update.emit("Logging...",0)
            IDnum = extractID(IDdata, IDregex)
            if not IDnum:
                continue
            #report ID
            self.update.emit(sheetReporter.Reporter().log(IDnum), 3)
            #ensure the ID isnt double logged
            IDnum = None
        self.readerDevice.ungrab()
        self.finished.emit()

    def USBworkerfinish(self):
        self.readerDevice.ungrab()