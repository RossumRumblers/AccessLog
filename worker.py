'''
USB Scanner Worker Thread Object Module
'''

import sheetReporter

from dependencies import USBFunc
from JSONReader import JSONReader
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

#regular expression for identifying ASU Student ID's
IDregex = r";601744(\d{10})\d(\d{10})\?"
# hardware ID's for the Scanner
device_IDs = ["5131", "2007"]


#
# some code from http://stackoverflow.com/a/33453124
#
class Worker(QObject):
    '''
    Creates a worker thread for interfacing with the device reader independently of the GUI.
    '''

    # create signal emitters
    _finished = pyqtSignal()
    updateStatus = pyqtSignal(str, int)
    Alert = pyqtSignal(str, str)

    # declare objects
    _readerDevice = None
    _mainWindow = None

    def __init__(self, mainWindow):
        QObject.__init__(self)
        self._mainWindow = mainWindow
        self._readerDevice = None

    @pyqtSlot()
    def USBworker(self):
        '''
        Worker Thread function
        '''
        try:
            self._readerDevice = USBFunc.Reader(device_IDs[0], device_IDs[1])
            self._readerDevice.grabDevice()
        except USBFunc.Reader.InitError as e:
            self.Alert.emit('crit', e.message)
            self._finished.emit()
            return

        while True:
            # retrieve data from card scanner
            # this command will hold execution until data is returned from the  card reader
            keyEvents = self._readerDevice.readData()
            try:
                IDdata = self._readerDevice.interpretEvents(keyEvents)
            except KeyError as e:
                self.Alert.emit('warn', e.message)
            self.updateStatus.emit("Logging...", 0)

            # get ID from regex
            IDnum = self._readerDevice.extractID(IDdata, IDregex)
            if not IDnum:
                # ID was not returned, possibly not ASU ID.
                self.updateStatus.emit("Please Scan only an ASU ID.", 3)
            else:
                # get club Identifier from the Name on the RadioButton
                clubName = self._mainWindow.getSelectedRadio()
                self._mainWindow.setSelectedRadio(clubName)

                # get Long Club Name
                clubID = None
                for club in JSONReader().getClubList():
                    if JSONReader().getClubNameLong(club) == clubName:
                        clubID = club
                        break

                if not JSONReader().getClubAllowed(clubID):
                    # members of this clube are not allowed to sign in
                    self.Alert.emit('crit', 'This club is currently not allowed to register.\n\
                        Please see John Alden or your club officers about this.')
                else:
                    # report ID and return update
                    try:
                        self.updateStatus.emit(sheetReporter.Reporter().log(IDnum, clubID), 3)
                    except Exception as e:
                        # Theres like...a ton of things that can go wrong here...
                        # Until i can figure them all just throw all errors
                        self.Alert.emit('crit', e.message)
                        self.updateStatus.emit('Nothing logged due to Error', 3)

            # ensure the ID isnt double logged
            IDnum = None
            IDdata = None

        # Should the loop ever exit, ungrab the device and call the worker finish function
        self._finished.emit()

    def USBworkerfinish(self):
        try:
            self._readerDevice.ungrabDevice()
        except USBFunc.Reader.InitError as e:
            self.Alert.emit('crit', e.message)
