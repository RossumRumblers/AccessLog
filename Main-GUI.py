#
# Version 2.0.1B
#

import re
import sys
import worker
import mainWindow
import JSONReader
import sheetReporter
from dependencies.miscFunc import *
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QMainWindow, QDesktopWidget, QRadioButton


class Form(QMainWindow, mainWindow.Ui_MainWindow):

	def __init__(self, parent=None):
		if not testRoot():
			print("Please rerun this script with root.")
			sys.exit()
		if not testInternet():
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
		self.workerobj._updateStatus.connect(self.updateStatus) # connect the update emitter to the onUpdate function
		self.wThread.started.connect(self.workerobj.USBworker)  # on thread started: run the USBworker function
		self.wThread.start()                                    # start the worker thread

		self.lineEdit.returnPressed.connect(self.pushButton.click)
		self.pushButton.clicked.connect(self.buttonPushed)

		self.show()


	def postSetup(self):
		self.setWindowFlags(Qt.FramelessWindowHint)
		frameGeo = self.frameGeometry()
		frameGeo.moveCenter(QDesktopWidget().availableGeometry().center())
		self.move(frameGeo.topLeft())
		i = 0
		for radio in self.findChildren(QRadioButton):
			try:
				elem = JSONReader.JSONReader().getClubNameLong(JSONReader.JSONReader().getClubList()[i])
				radio.setText(elem)
			except(IndexError):
				radio.hide()
			i+=1

	def W_onFinished(self):
		self.wThread.quit()
		self.obj.USBworkerfinish()

	def buttonPushed(self):
		IDnum = self.lineEdit.text()
		if(IDnum == ""):
			self.updateStatus("Please Enter an ASU ID", 3)
		else:
			self.updateStatus("Logging...", 0)
			self.lineEdit.setText("")
			if len(IDnum) == 10 and IDnum.isdigit():
				clubName = self.getSelectedRadio()
				self.setSelectedRadio(clubName)
				clubID = None
				for club in JSONReader.JSONReader().getClubList():
					if(JSONReader.JSONReader().getClubNameLong(club) == clubName):
						clubID = club
				self.updateStatus(sheetReporter.Reporter().log(IDnum, clubID), 3)
			else:
				self.updateStatus("Please Enter an ASU ID", 3)

	def getSelectedRadio(self):
		for radio in self.findChildren(QRadioButton):
			if(radio.isChecked()):
				text = radio.text()
				print(text)
				return text

	def setSelectedRadio(self, name):
		for radio in self.findChildren(QRadioButton):
			if name == radio.text():
				radio.setChecked(True)

	def updateStatus(self, message, time):
		'''time is in seconds'''
		self.statusBar.showMessage(message, time*1000)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	form = Form()
	app.exec_()
	sys.exit()