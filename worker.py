import time
import evdev
import mainWindow
import JSONReader
import sheetReporter
from dependencies.USBFunc import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

#regular expression for identifying ASU Student ID's
IDregex = ";601744(\d{10})\d(\d{10})\?"
# hardware ID's for the Scanner
device_IDs = ["5131","2007"]


#
# some code from http://stackoverflow.com/a/33453124
#
class Worker(QObject):
	# create emitters
	_finished = pyqtSignal()
	_updateStatus = pyqtSignal(str,int)
	_readerDevice = None
	_mainWindow = None

	def __init__(self, mainWindow):
		QObject.__init__(self)
		self._mainWindow = mainWindow
		self._readerDevice = initReader(device_IDs[0], device_IDs[1])

	@pyqtSlot()
	def USBworker(self):
		if not self._readerDevice:
			self._finished.emit()
		self._readerDevice.grab()
		while(True):
			# retrieve data from card scanner
			IDdata = interpretEvents(readData(self._readerDevice))
			self._updateStatus.emit("Logging...", 0)
			IDnum = extractID(IDdata, IDregex)
			if not IDnum:
				#ID was not returned, possibly not ASU ID.
				self._updateStatus.emit("Please Scan only an ASU ID.", 3)

			else:
				#get club Identifier from the Name on the RadioButton
				clubName = self._mainWindow.getSelectedRadio()
				clubID = None
				for club in JSONReader.JSONReader().getClubList():
					if(JSONReader.JSONReader().getClubNameLong(club) == clubName):
						clubID = JSONReader.JSONReader().getClubNameShort(club)
				#report ID
				self._updateStatus.emit(sheetReporter.Reporter().log(IDnum, clubID), 3)
			#ensure the ID isnt double logged
			IDnum = None
			IDdata = None
		self._readerDevice.ungrab()
		self._finished.emit()

	def USBworkerfinish(self):
		self._readerDevice.ungrab()