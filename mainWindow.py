# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
#
import sheetReporter
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):

    def __init__(self):
        self.setupUi(self)
    
    def _buttonPushed(self):
        IDnum = self.lineEdit.text()
        self.lineEdit.setText("")
        IDnum = extractID(IDnum, "\d{10}"):
        if IDnum:
            sheetReporter.Reporter().log(IDnum)
            

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(590, 270)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(590, 270))
        MainWindow.setMaximumSize(QtCore.QSize(590, 270))
        MainWindow.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 570, 20))
        font = QtGui.QFont()
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(10, 140, 570, 110))
        self.textEdit.setReadOnly(True)
        self.textEdit.setAcceptRichText(False)
        self.textEdit.setCursorWidth(1)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.returnPressed.connect(self.pushButton.click)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(215, 70, 161, 61))
        self.widget.setObjectName("widget")
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setGeometry(QtCore.QRect(0, 30, 100, 20))
        self.lineEdit.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.lineEdit.setMouseTracking(False)
        self.lineEdit.setAcceptDrops(False)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setGeometry(QtCore.QRect(110, 30, 51, 20))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self._buttonPushed)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setGeometry(QtCore.QRect(0, 10, 160, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setIndent(-1)
        self.label_3.setObjectName("label_3")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(0, 50, 581, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setIndent(-1)
        self.label_2.setObjectName("label_2")
        #MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Rossum Rumblers Log App"))
        self.label.setText(_translate("MainWindow", "Please Scan your ASU ID Card"))
        self.pushButton.setText(_translate("MainWindow", "Submit"))
        self.label_3.setText(_translate("MainWindow", "Enter Your ASU ID:"))
        self.label_2.setText(_translate("MainWindow", "OR"))

