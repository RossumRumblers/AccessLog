import mainWindow
from time import strftime
from datetime import datetime
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

#
# some code from http://stackoverflow.com/a/33453124
#
class Debug(QObject):
	# create emitters
	finished = pyqtSignal()
	update = pyqtSignal(str)

	@pyqtSlot()
	def Debugworker(self):
		lastlog = datetime.now()
		strftime("%Y-%m-%d %H:%M:%S")
		while(True):
			delta = datetime.now() - lastlog
			if delta.seconds == 300:
				lastlog = datetime.now()
				print("Keep Alive: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
				continue
			else:
				continue
		self.finished.emit()