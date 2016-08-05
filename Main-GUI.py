from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout
import sys
import worker
import mainWindow
import sheetReporter


class Form(QWidget, mainWindow.Ui_MainWindow):

    def __init__(self, parent=None):
        # init Mainwindow class
        super().__init__()
        mainWindow = super(Form, self).__init__(parent)
        # init the google API
        sheetReporter.Reporter()

        #
        # code from http://stackoverflow.com/a/33453124
        #
        self.obj = worker.Worker()                         # instatiate worker object
        self.wThread = QThread()                           # instatiate worker thread
        self.obj.update.connect(self.onUpdate)             # connect the update emitter to the onUpdate function
        self.obj.moveToThread(self.wThread)                # move the worker object into the worker thread
        self.obj.finished.connect(self.onfinished)         # connect the finished emitter to the kill thread function
        self.wThread.started.connect(self.obj.USBworker)   # on thread start run the USBworker function
        self.wThread.start()                               # start the worker thread
        self.show()                                        # showUI
        
    ###TODO###
    # update the bottom textbox with relevant info
    def onUpdate(self):
        pass

    def onfinished(self):
        self.wThread.quit()
        self.obj.USBworkerfinish()
        

###TODO###
# test root before runnning
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    print(app.exec_())
    form.onfinished()
    sys.exit()