from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout
import sys
import worker
import mainWindow
import SheetReporter


class Form(QWidget, mainWindow.Ui_MainWindow):

    def __init__(self, parent=None):
        # init Mainwindow class
        super().__init__()
        #re-init mainwindow class???
        mainWindow = super(Form, self).__init__(parent)
        # init the google API
        SheetReporter.Reporter()

        
        self.obj = worker.Worker()                            # instatiate worker object
        self.workerthread = QThread()                         # instatiate worker thread
        self.obj.update.connect(self.onUpdate)                # connect the update emitter to the onUpdate function
        self.obj.moveToThread(self.workerthread)              # move the worker object into the worker thread
        self.obj.finished.connect(self.thread.quit)           # connect the finished emitter to the kill thread function
        self.workerthread.started.connect(self.obj.USBworker) # on thread start run the USBworker function
        self.workerthread.start()                             # start the worker thread
        self.initUI()                                         # create UI

    def initUI(self):
        self.show()
    ###TODO###
    # update the bottom textbox with relevant info
    def onUpdate(self, IDnum):
        pass
        

###TODO###
# test root
if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    sys.exit(app.exec_())