# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'l8_lst_swa_settings_ui.ui'
#
# Created: Wed Jan 20 02:14:41 2016
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(315, 361)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/Landsat8LST_SWA/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout_4 = QtGui.QGridLayout(Dialog)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.applyButton = QtGui.QPushButton(Dialog)
        self.applyButton.setObjectName(_fromUtf8("applyButton"))
        self.gridLayout_4.addWidget(self.applyButton, 3, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 2, 2, 1, 1)
        self.TLEAutoButton = QtGui.QPushButton(self.groupBox)
        self.TLEAutoButton.setObjectName(_fromUtf8("TLEAutoButton"))
        self.gridLayout_2.addWidget(self.TLEAutoButton, 2, 3, 1, 1)
        self.TLELine2 = QtGui.QLineEdit(self.groupBox)
        self.TLELine2.setObjectName(_fromUtf8("TLELine2"))
        self.gridLayout_2.addWidget(self.TLELine2, 1, 1, 1, 3)
        self.TLELine1 = QtGui.QLineEdit(self.groupBox)
        self.TLELine1.setObjectName(_fromUtf8("TLELine1"))
        self.gridLayout_2.addWidget(self.TLELine1, 0, 1, 1, 3)
        self.gridLayout_4.addWidget(self.groupBox, 1, 0, 1, 4)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.MRTSwathBinDirLine = QtGui.QLineEdit(self.groupBox_2)
        self.MRTSwathBinDirLine.setObjectName(_fromUtf8("MRTSwathBinDirLine"))
        self.gridLayout.addWidget(self.MRTSwathBinDirLine, 0, 1, 1, 1)
        self.MRTSwathBinDirButton = QtGui.QPushButton(self.groupBox_2)
        self.MRTSwathBinDirButton.setObjectName(_fromUtf8("MRTSwathBinDirButton"))
        self.gridLayout.addWidget(self.MRTSwathBinDirButton, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.MRTSwathDataDirLine = QtGui.QLineEdit(self.groupBox_2)
        self.MRTSwathDataDirLine.setObjectName(_fromUtf8("MRTSwathDataDirLine"))
        self.gridLayout.addWidget(self.MRTSwathDataDirLine, 1, 1, 1, 1)
        self.MRTSwathDataDirButton = QtGui.QPushButton(self.groupBox_2)
        self.MRTSwathDataDirButton.setObjectName(_fromUtf8("MRTSwathDataDirButton"))
        self.gridLayout.addWidget(self.MRTSwathDataDirButton, 1, 2, 1, 1)
        self.label_7 = QtGui.QLabel(self.groupBox_2)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.downloadsDirLine = QtGui.QLineEdit(self.groupBox_2)
        self.downloadsDirLine.setObjectName(_fromUtf8("downloadsDirLine"))
        self.gridLayout.addWidget(self.downloadsDirLine, 2, 1, 1, 1)
        self.downloadsDirButton = QtGui.QPushButton(self.groupBox_2)
        self.downloadsDirButton.setObjectName(_fromUtf8("downloadsDirButton"))
        self.gridLayout.addWidget(self.downloadsDirButton, 2, 2, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 0, 0, 1, 4)
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_5 = QtGui.QLabel(self.groupBox_3)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.SpacetrackLoginLine = QtGui.QLineEdit(self.groupBox_3)
        self.SpacetrackLoginLine.setObjectName(_fromUtf8("SpacetrackLoginLine"))
        self.gridLayout_3.addWidget(self.SpacetrackLoginLine, 0, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_3)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1)
        self.SpaceTrackPasswordLine = QtGui.QLineEdit(self.groupBox_3)
        self.SpaceTrackPasswordLine.setEchoMode(QtGui.QLineEdit.Password)
        self.SpaceTrackPasswordLine.setObjectName(_fromUtf8("SpaceTrackPasswordLine"))
        self.gridLayout_3.addWidget(self.SpaceTrackPasswordLine, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(132, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 3, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Settings", None))
        self.applyButton.setText(_translate("Dialog", "OK", None))
        self.groupBox.setTitle(_translate("Dialog", "MODIS TLE for date", None))
        self.label_3.setText(_translate("Dialog", "TLE Line 1", None))
        self.label_4.setText(_translate("Dialog", "TLE Line 2", None))
        self.TLEAutoButton.setText(_translate("Dialog", "Auto", None))
        self.groupBox_2.setTitle(_translate("Dialog", "MRTSwath settings", None))
        self.label.setText(_translate("Dialog", "MRTSwath bin directory", None))
        self.MRTSwathBinDirButton.setText(_translate("Dialog", "...", None))
        self.label_2.setText(_translate("Dialog", "MRTSwath data directory", None))
        self.MRTSwathDataDirButton.setText(_translate("Dialog", "...", None))
        self.label_7.setText(_translate("Dialog", "Directory for downloads", None))
        self.downloadsDirButton.setText(_translate("Dialog", "...", None))
        self.groupBox_3.setTitle(_translate("Dialog", "Space-track.org credentials", None))
        self.label_5.setText(_translate("Dialog", "Login", None))
        self.label_6.setText(_translate("Dialog", "Password", None))
