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
import l8_lst_swa_common_lib
import os
import modis_water_vapor_interface

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
        self.connect(self.ui.satTabDataTypeRawRadioButton, QtCore.SIGNAL("clicked()"), self.satTabChangeDataType)
        self.connect(self.ui.satTabCorrectedRadioButton, QtCore.SIGNAL("clicked()"), self.satTabChangeDataType)
        self.connect(self.ui.satTabToolBox, QtCore.SIGNAL("currentChanged(int)"), self.satTabChangeRadioButtons)
        self.ui.satTabAqDateTime.dateChanged.connect(self.correctedDateChanged)

        ### Ground data tab
        self.connect(self.ui.LSEClassifiedRadioButton, QtCore.SIGNAL("clicked()"), self.LSETypeChange)
        self.connect(self.ui.LSENDVIRadioButton, QtCore.SIGNAL("clicked()"), self.LSETypeChange)
        self.connect(self.ui.LSEGRIDRadioButton, QtCore.SIGNAL("clicked()"), self.LSETypeChange)


        ### Output tab
        self.connect(self.ui.outputLSTBrowseButton, QtCore.SIGNAL("clicked()"), self.outputBrowse)
        self.connect(self.ui.outputLSTCheckButton, QtCore.SIGNAL("clicked()"), self.outputCheck)

        ##### FILL COMBOBOXES
        rasterLayers = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values() if
                          (layer.type() == QgsMapLayer.RasterLayer)]
        self.ui.satTabB10ComboBox.addItems(rasterLayers)
        self.ui.satTabB11ComboBox.addItems(rasterLayers)
        self.ui.satTabNDVIComboBox.addItems(rasterLayers)
        self.ui.waterVaporGRIDComboBox.addItems(rasterLayers)
        self.ui.LSEGRIDComboBox.addItems(rasterLayers)
        self.ui.LSEClassifiedRasterComboBox.addItems(rasterLayers)



        #print modis_water_vapor_interface.downloadMODL2ForGivenDateAndTime(2013,2,5,'0105','MOD03','E:\\lol.hdf')

    ##############################################################
    ################ INTERFACE
    ##############################################################

    def readyInterface(self):
        self.ui.progressBar.setVisible(False)
        self.ui.processLabel.setText('No active processes')
        self.ui.tabWidget.setEnabled(True)

    def busyInterface(self):
        self.ui.progressBar.setVisible(True)
        self.ui.tabWidget.setDisabled(True)

    def satTabChangeDataType(self):
        if self.ui.satTabDataTypeRawRadioButton.isChecked():
            self.ui.satTabToolBox.setCurrentIndex(0)
        else:
            self.ui.satTabToolBox.setCurrentIndex(1)

    def satTabChangeRadioButtons(self):
        if self.ui.satTabToolBox.currentIndex() == 0:
            self.ui.satTabDataTypeRawRadioButton.setChecked(True)
        else:
            self.ui.satTabCorrectedRadioButton.setChecked(True)

    def LSETypeChange(self):
        if self.ui.LSEClassifiedRadioButton.isChecked():
            self.ui.LSEClassificationGroupBox.setEnabled(True)
        if self.ui.LSENDVIRadioButton.isChecked():
            self.ui.LSEClassificationGroupBox.setDisabled(True)
        if self.ui.LSEGRIDRadioButton.isChecked():
            self.ui.LSEClassificationGroupBox.setDisabled(True)

    def correctedDateChanged(self):
        self.currentDate = self.ui.satTabAqDateTime.date().toString("dd.MM.yyyy")

    # Open settings for MOD09 Retrieving
    def openModisSettings(self):
        self.ModisSettings = l8_lst_swa_settings.L8_lst_swaSettingsDlg()
        self.ModisSettings.show()

    def outputBrowse(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save file', '', '*.tif')
        if filename:
            self.ui.outputLSTLine.setText(filename)
        pass

    ##############################################################
    ################ END INTERFACE
    ##############################################################

    ##############################################################
    ################ CHECK INPUTS
    ##############################################################

    def outputCheck(self):
        if not self.ui.outputLSTLine.text():
            QtGui.QMessageBox.critical(None, "Error", 'Output file not specified')
            self.readyInterface()
            return

        outputPath = self.ui.outputLSTLine.text()
        if l8_lst_swa_common_lib.isWritable(os.path.dirname(outputPath)):
            self.ui.statusOutputCheckBox.setChecked(True)
        else:
            QtGui.QMessageBox.critical(None, "Error", 'Output path is not writable!')
            self.readyInterface()
            return
    ##############################################################
    ################ END CHECK INPUTS
    ##############################################################

    # Close window by pressing "Cancel" button
    def cancel(self):
        #TEST
        landsat = l8_lst_swa_common_lib.getLayerByName('B4_reflectance')
        print modis_water_vapor_interface.getWaterVaporForGivenRaster(landsat,2013,7,2,'s','1 25994U 99068A   13183.23066698  .00000248  00000-0  65149-4 0  9990','2 25994 098.2058 257.9549 0001580 091.8015 268.3387 14.57122310720105', self.ui.processLabel, 'E:\\modistests')
        #self.close()