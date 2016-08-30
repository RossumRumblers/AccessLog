import re
import sys
import debug
import worker
import mainWindow
import sheetReporter
from datetime import datetime
from dependencies.miscFunc import *
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QMainWindow, QDesktopWidget


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
		self.workerobj = worker.Worker()                        # instatiate worker object
		self.wThread = QThread()                                # instatiate worker thread
		self.workerobj.moveToThread(self.wThread)               # move the worker object into the worker thread
		self.workerobj.update.connect(self.W_onUpdate)          # connect the update emitter to the onUpdate function
		self.workerobj.finished.connect(self.W_onFinished)      # connect the finished emitter to the kill thread function
		self.wThread.started.connect(self.workerobj.USBworker)  # on thread start run the USBworker function
		self.wThread.start()                                    # start the worker thread

		self.debugobj = debug.Debug()                           # instatiate worker object
		self.dThread = QThread()                                # instatiate worker thread
		self.debugobj.moveToThread(self.dThread)               # move the worker object into the worker thread
		self.debugobj.update.connect(self.D_onUpdate)          # connect the update emitter to the onUpdate function
		self.debugobj.finished.connect(self.D_onFinished)      # connect the finished emitter to the kill thread function
		self.dThread.started.connect(self.debugobj.Debugworker)  # on thread start run the USBworker function
		self.dThread.start()                                    # start the worker thread

		self.lineEdit.returnPressed.connect(self.pushButton.click)
		self.pushButton.clicked.connect(self.buttonPushed)

		self.show()


	def postSetup(self):
		self.setWindowFlags(Qt.FramelessWindowHint)
		frameGeo = self.frameGeometry()
		frameGeo.moveCenter(QDesktopWidget().availableGeometry().center())
		self.move(frameGeo.topLeft())

	def W_onUpdate(self, string, time):
		self.updateStatus(string, time)

	def W_onFinished(self):
		self.wThread.quit()
		self.obj.USBworkerfinish()

	def D_onUpdate(string):
		print(string)

	def D_onFinished(self):
		self.dThread.quit()

	def buttonPushed(self):
		IDnum = self.lineEdit.text()
		if(IDnum == ""):
			self.updateStatus("Please Enter an ASU ID", 3)
		else:
			self.updateStatus("Logging...", 0)
			self.lineEdit.setText("")
			if len(IDnum) == 10 and IDnum.isdigit():
				self.updateStatus(sheetReporter.Reporter().log(IDnum), 3)
			else:
				self.updateStatus("Please Enter an ASU ID", 3)

	def updateStatus(self, message, time):
		# time is in seconds
		self.statusBar.showMessage(message, time*1000)


###TODO###
# test root before runnning
if __name__ == '__main__':
	print("\nScript run at ", datetime.now(), "\n=========================================")
	app = QApplication(sys.argv)
	form = Form()
	app.exec_()
	sys.exit()