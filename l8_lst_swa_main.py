# -*- coding: utf-8 -*-
"""
/***************************************************************************
Landsat 8 LST Retriever (SWA)
                                 A QGIS plugin
This module allows to retrieve Land Surface Temperature (LST) from Landsat 8 data (TIRS channels)
using Split-Windows Algorithm. Water Vapor content and Land Surface Emissivity needed, but both
could be recieved automatically in module (Water vapor via MODIS MOD09, LSE via NDVI).

                              -------------------
        begin                : 2016-01-16
        copyright            : (C) 2016 by Eduard Kazakov
        email                : silenteddie@gmail.com
        homepage             : http://ekazakov.info
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtGui import QApplication

from ui import l8_lst_swa_main_ui, l8_lst_swa_settings_ui
import l8_lst_swa_settings
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QVariant
from qgis.core import *
from qgis.core import QgsMapLayerRegistry
import resources

class L8_lst_swaMainDlg(QtGui.QWidget):

    currentDate = '01.01.2000'

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = l8_lst_swa_main_ui.Ui_Dialog()
        self.ui.setupUi(self)

        self.readyInterface()

        ##### BUTTON HANDLERS

        ### Common
        self.connect(self.ui.closeButton, QtCore.SIGNAL("clicked()"), self.cancel)

        ### Satellite data tab
        self.connect(self.ui.waterVaporMODISSettings, QtCore.SIGNAL("clicked()"), self.openModisSettings)

    def readyInterface(self):
        self.ui.progressBar.setVisible(False)
        self.ui.processLabel.setText('No active processes')
        self.ui.tabWidget.setEnabled(True)

    def busyInterface(self):
        self.ui.progressBar.setVisible(True)
        self.ui.tabWidget.setDisabled(True)

    # Open settings for MOD09 Retrieving
    def openModisSettings(self):
        self.ModisSettings = l8_lst_swa_settings.L8_lst_swaSettingsDlg()
        self.ModisSettings.show()

    # Close window by pressing "Cancel" button
    def cancel(self):
        self.close()