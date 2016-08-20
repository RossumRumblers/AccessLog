import re
import sys
import worker
import mainWindow
import sheetReporter
from dependencies.miscFunc import *
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QMainWindow, QDesktopWidget


class Form(QMainWindow, mainWindow.Ui_MainWindow):

	def __init__(self, parent=None):
		QMainWindow.__init__(self)
		self.setupUi(self)
		self.postSetup()
		sheetReporter.Reporter() # init Google API

		#
		# worker thread code from http://stackoverflow.com/a/33453124
		#
		self.obj = worker.Worker()                        # instatiate worker object
		self.wThread = QThread()                          # instatiate worker thread
		self.obj.moveToThread(self.wThread)               # move the worker object into the worker thread
		self.obj.update.connect(self.W_onUpdate)          # connect the update emitter to the onUpdate function
		self.obj.finished.connect(self.W_onfinished)      # connect the finished emitter to the kill thread function
		self.wThread.started.connect(self.obj.USBworker)  # on thread start run the USBworker function
		self.wThread.start()                              # start the worker thread

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

	def W_onfinished(self):
		self.wThread.quit()
		self.obj.USBworkerfinish()

	def buttonPushed(self):
		IDnum = self.lineEdit.text()
		if(IDnum == ""):
			self.updateStatus("Please Enter an ASU ID", 3)
		else:
			self.updateStatus("Logging...", 0)
			self.lineEdit.setText("")
			p = re.compile("\d{10}")
			match = re.search(p, IDnum)
			if match:
				self.updateStatus(sheetReporter.Reporter().log(IDnum), 3)

	def updateStatus(self, message, time):
		# time is in seconds
		self.statusBar.showMessage(message, time*1000)


###TODO###
# test root before runnning
if __name__ == '__main__':
	if not testRoot():
		print("Please rerun this script with root.")
		sys.exit()
	if not testInternet():
		print("Please Verify this machine is connected to the internet.")
		sys.exit()
	app = QApplication(sys.argv)
	form = Form()
	print(app.exec_())
	form.W_onfinished()
	sys.exit()