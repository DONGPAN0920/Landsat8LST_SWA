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
from osgeo import gdal

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

        self.connect(self.ui.satTabMTLAddButton, QtCore.SIGNAL("clicked()"), self.mtlBrowse)
        self.connect(self.ui.satTabRawCheckButton, QtCore.SIGNAL("clicked()"), self.mtlCheck)


        ### Ground data tab


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



        #print modis_water_vapor_interface.downloadMODL2ForGivenDateAndTime(2013,2,5,'0105','MOD03','E:\\lol.hdf')

    ##############################################################
    ################ INTERFACE
    ##############################################################

    def readyInterface(self):
        """
        Set interface to input mode (unblock all, hide progress bar)
        """
        self.ui.progressBar.setVisible(False)
        self.ui.processLabel.setText('No active processes')
        self.ui.tabWidget.setEnabled(True)

    def busyInterface(self):
        """
        Set interface to busy mode (block all, show progress bar)
        """
        self.ui.progressBar.setVisible(True)
        self.ui.tabWidget.setDisabled(True)

    def satTabChangeDataType(self):
        """
        Change toolBox active tab when radiobutton is pressed
        """
        if self.ui.satTabDataTypeRawRadioButton.isChecked():
            self.ui.satTabToolBox.setCurrentIndex(0)
        else:
            self.ui.satTabToolBox.setCurrentIndex(1)

    def satTabChangeRadioButtons(self):
        """
        Change active radioButtom when toolBox active tab is changed
        """
        if self.ui.satTabToolBox.currentIndex() == 0:
            self.ui.satTabDataTypeRawRadioButton.setChecked(True)
        else:
            self.ui.satTabCorrectedRadioButton.setChecked(True)

    def correctedDateChanged(self):
        """
        If aquisition date changed
        """
        self.currentDate = self.ui.satTabAqDateTime.date().toString("dd.MM.yyyy")

    def openModisSettings(self):
        """
        Open settings for MOD09 Retrieving
        """
        self.ModisSettings = l8_lst_swa_settings.L8_lst_swaSettingsDlg()
        self.ModisSettings.show()

    def outputBrowse(self):
        """
        Open browse dialog for output file selecting
        """
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save file', '', '*.tif')
        if filename:
            self.ui.outputLSTLine.setText(filename)
        pass

    def mtlBrowse (self):
        """
        Open browse dialog for metadata file selecting
        """
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '', '*.txt')
        if filename:
            self.ui.satTabMTLPathLine.setText(filename)
        pass

    ##############################################################
    ################ END INTERFACE
    ##############################################################

    ##############################################################
    ################ CHECK INPUTS
    ##############################################################

    def outputCheck(self):
        """
        Check if output settings are correct
        """
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

    def mtlCheck(self):
        """
        Check if metadata file is correct and all scenes are available
        """
        if not self.ui.satTabMTLPathLine.text():
            QtGui.QMessageBox.critical(None, "Error", 'Input MTL file not specified')
            return
        metadataPath = self.ui.satTabMTLPathLine.text()
        metadataBasePath = os.path.dirname(metadataPath)
        # Check if all files available
        try:
            mtl_dict = l8_lst_swa_common_lib.readBasicMetadata(metadataPath)
        except:
            QtGui.QMessageBox.critical(None, "Error", 'Invalid metadata')
            self.readyInterface()
            return

        # Check if extra data available
        #if not (os.path.isfile(metadataBasePath + '/' + mtl_dict['mtl_band4']) and os.path.isfile(
        #                metadataBasePath + '/' + mtl_dict['mtl_band5']) and os.path.isfile(
        #                metadataBasePath + '/' + mtl_dict['mtl_band10']) and os.path.isfile(metadataBasePath + '/' + mtl_dict['mtl_band11'])):
        #    QtGui.QMessageBox.critical(None, "Error", 'Some of needed landsat files not exists')
        #    return

        self.ui.statusSatelliteCheckBox.setChecked(True)



    ##############################################################
    ################ END CHECK INPUTS
    ##############################################################

    ##############################################################
    ################ PROCESSING
    ##############################################################

    def prepareRawLandsat(self):
        """
        Get path to scenes from metadata and convert all to radiance
        """
        metadataPath = self.ui.satTabMTLPathLine.text()
        mtl_dict = l8_lst_swa_common_lib.readBasicMetadata(metadataPath)
        metadataBasePath = os.path.dirname(metadataPath)

        ### B4, B5, B10, B11 to radiance
        B4Radiance = l8_lst_swa_common_lib.Landsat8_DN_to_radiance(1,metadataBasePath + '/' + mtl_dict['mtl_band4'],4,metadataPath)
        B5Radiance = l8_lst_swa_common_lib.Landsat8_DN_to_radiance(1,metadataBasePath + '/' + mtl_dict['mtl_band5'],5,metadataPath)
        B10Radiance = l8_lst_swa_common_lib.Landsat8_DN_to_radiance(1,metadataBasePath + '/' + mtl_dict['mtl_band10'],10,metadataPath)
        B11Radiance = l8_lst_swa_common_lib.Landsat8_DN_to_radiance(1,metadataBasePath + '/' + mtl_dict['mtl_band11'],11,metadataPath)

        ### NDVI Array
        #NDVIArray = (B5Radiance - B4Radiance) / (B5Radiance + B4Radiance)


    def cancel(self):
        """
        Close window by pressing "Cancel" button
        """
        self.close()