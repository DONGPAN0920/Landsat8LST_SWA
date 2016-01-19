# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'l8_lst_swa_about_ui.ui'
#
# Created: Wed Jan 20 01:43:20 2016
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
        Dialog.resize(296, 313)
        Dialog.setMinimumSize(QtCore.QSize(291, 300))
        Dialog.setMaximumSize(QtCore.QSize(554, 383))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/Landsat8LST_SWA/help.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.scrollArea = QtGui.QScrollArea(Dialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 276, 249))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_3.setWordWrap(True)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "About", None))
        self.label.setText(_translate("Dialog", "Landsat 8 LST Retriever (SWA)", None))
        self.label_2.setText(_translate("Dialog", "ver. 1.0", None))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Landsat 8 LST Retriever (SWA) module</span></p><p>This module allows to retrieve Land Surface Temperature (LST) from Landsat 8 data (TIRS channels) using Split-Windows Algorithm. Water Vapor content and Land Surface Emissivity needed, but both could be recieved automatically in module (Water vapor via MODIS MOD09, LSE via NDVI).</p><p><span style=\" font-size:9pt;\">You can send your suggestions on silenteddie@gmail.com</span></p><p><span style=\" font-size:9pt;\">Modis Track L1 L2 - Licence GNU GPL 2</span></p><p><span style=\" font-size:9pt;\">Written in 2016 by Eduard Kazakov (</span><a href=\"http://www.ekazakov.info\"><span style=\" font-size:9pt; text-decoration: underline; color:#0000ff;\">ekazakov.info</span></a><span style=\" font-size:9pt;\">)</span></p></body></html>", None))
