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


class Worker(QObject):

    def __init__(self):
        # create emitters
        self.finished = pyqtSignal()
        self.update = pyqtSignal(String)
        # init reader
        self.readerDevice = initReader(device_IDs[0], device_IDs[1])

    @pyqtSlot()
    def USBworker(self):
        IDnum = None

        while(True):
            IDnum = extractID(interpretEvents(readData(readerDevice)), IDregex)
            if not IDnum:
                continue
            sheetReporter.Reporter().log(IDnum)
            self.update.emit()
        self.finished.emit()