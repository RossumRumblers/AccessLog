import re
import sys
import worker
import mainWindow
import sheetReporter
from dependencies import *
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QMainWindow


class Form(QMainWindow, mainWindow.Ui_MainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.setupUi(self)
        sheetReporter.Reporter() # init Google API

        #
        # worker thread code from http://stackoverflow.com/a/33453124
        #
        self.obj = worker.Worker()                         # instatiate worker object
        self.wThread = QThread()                           # instatiate worker thread
        self.obj.moveToThread(self.wThread)                # move the worker object into the worker thread
        self.obj.update.connect(self.onUpdate)             # connect the update emitter to the onUpdate function
        self.obj.finished.connect(self.onfinished)         # connect the finished emitter to the kill thread function
        self.wThread.started.connect(self.obj.USBworker)   # on thread start run the USBworker function
        self.wThread.start()                               # start the worker thread

        self.lineEdit.returnPressed.connect(self.pushButton.click)
        self.pushButton.clicked.connect(self.buttonPushed)

        self.show()

    ###TODO###
    # update statusbar with status message
    def onUpdate(self):
        pass

    def onfinished(self):
        self.wThread.quit()
        self.obj.USBworkerfinish()
        
    ###TODO###
    # update statusbar with status message
    def buttonPushed(self):
        self.statusBar.showMessage("LOL")
        IDnum = self.lineEdit.text()
        self.lineEdit.setText("")
        p = re.compile("\d{10}")
        match = re.search(p, IDnum)
        if match:
            sheetReporter.Reporter().log(IDnum)
            
    def updateStatus(self, string):
        self.statusBar.showMessage(string)
  

###TODO###
# test root before runnning
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    print(app.exec_())
    form.onfinished()
    sys.exit()