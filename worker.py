import time
import evdev
import mainWindow
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
			IDdata = interpretEvents(readData(self.readerDevice))
			print("Card Scanned ", IDdata)
			self.update.emit("Logging...", 0)
			print("emitted Logging ")
			IDnum = extractID(IDdata, IDregex)
			print("Card Scanned ", IDnum)
			if not IDnum:
				print("IDnum DNE ")
				self.update.emit("Please Scan only an ASU ID.", 3)
				print("Emitted non-valid")
				continue
			else:
				print("IDnum E ")
				#report ID
				self.update.emit(sheetReporter.Reporter().log(IDnum), 3)
				print("LOG IDnum")
			#ensure the ID isnt double logged
			IDnum = None
			IDdata = None
			print("Clearing Data, restarting")
		self.readerDevice.ungrab()
		self.finished.emit()

	def USBworkerfinish(self):
		self.readerDevice.ungrab()