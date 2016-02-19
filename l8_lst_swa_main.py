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
import gc

import re
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
import l8_lst_swa_core
import numpy as np

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
        self.connect(self.ui.runButton, QtCore.SIGNAL("clicked()"), self.run)

        ### Satellite data tab
        self.connect(self.ui.waterVaporMODISSettings, QtCore.SIGNAL("clicked()"), self.openModisSettings)
        self.connect(self.ui.satTabDataTypeRawRadioButton, QtCore.SIGNAL("clicked()"), self.satTabChangeDataType)
        self.connect(self.ui.satTabCorrectedRadioButton, QtCore.SIGNAL("clicked()"), self.satTabChangeDataType)
        self.connect(self.ui.satTabToolBox, QtCore.SIGNAL("currentChanged(int)"), self.satTabChangeRadioButtons)
        self.ui.satTabAqDateTime.dateChanged.connect(self.correctedDateChanged)

        self.connect(self.ui.satTabMTLAddButton, QtCore.SIGNAL("clicked()"), self.mtlBrowse)
        self.connect(self.ui.satTabRawCheckButton, QtCore.SIGNAL("clicked()"), self.mtlCheck)

        ### Meteo data tab
        self.connect(self.ui.waterVaporCheckButton, QtCore.SIGNAL("clicked()"), self.meteoCheck)

        ### Ground data tab
        self.connect(self.ui.LSECheckButton, QtCore.SIGNAL("clicked()"), self.groundCheck)

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



        ############ TESTING

        self.ui.satTabMTLPathLine.setText('E:/Landsat8_urban/Petersburg_24_08_15/LC81850182015236LGN00/LC81850182015236LGN00_MTL.txt')
        self.ui.outputLSTLine.setText('E:/sss.tif')

        ####################

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

    def groundCheck(self):
        """
        Check if ground data is correct
        """
        if self.ui.LSENDVIRadioButton.isChecked():
            self.ui.statusGroundCheckBox.setChecked(True)

    def meteoCheck(self):
        """
        Check if ground data is correct
        """
        if self.ui.waterVaporGRIDRadioButton.isChecked():
            if self.ui.waterVaporGRIDComboBox.currentText():
                self.ui.statusMeteoCheckBox.setChecked(True)

    ##############################################################
    ################ END CHECK INPUTS
    ##############################################################

    ##############################################################
    ################ PROCESSING
    ##############################################################

    def getInputs(self):
        tempPath = os.path.dirname(os.path.abspath(__file__)) + '\\temp\\'
        if self.ui.satTabDataTypeRawRadioButton.isChecked():
            metadataPath = self.ui.satTabMTLPathLine.text()
            metadataBasePath = os.path.dirname(metadataPath)
            mtl_dict, B10BrightnessTemperature, B11BrightnessTemperature, LSE10Array, LSE11Array = self.prepareRawLandsat()
            #print 'lol'

        if self.ui.waterVaporGRIDRadioButton.isChecked():
            #print 'adj'
            baseRasterPath = re.sub("^\s+|\n|\r|\s+$", '', metadataBasePath + '/' + mtl_dict['mtl_band10'])
            baseRaster = QgsRasterLayer(baseRasterPath,'B10 Base Layer')
            #print baseRaster.isValid()
            #print baseRaster.extent()
            waterVaporSourceRaster = l8_lst_swa_common_lib.getLayerByName(self.ui.waterVaporGRIDComboBox.currentText())
            #print waterVaporSourceRaster.isValid()
            l8_lst_swa_common_lib.adjustRasterToBaseRaster(baseRaster,waterVaporSourceRaster,tempPath + 'waterVapor.tif')
            waterVapor = gdal.Open (tempPath + 'waterVapor.tif')
            waterVaporArray = np.array(waterVapor.GetRasterBand(1).ReadAsArray().astype(np.float32))

        print waterVaporArray.shape
        print B10BrightnessTemperature.shape
        print B11BrightnessTemperature.shape
        print LSE10Array.shape
        print LSE11Array.shape

        #LSTArray = l8_lst_swa_core.getLSTWithSWAForArray(waterVaporArray,LSE10Array,LSE11Array,B10BrightnessTemperature,B11BrightnessTemperature)
        LSTArray = (B10BrightnessTemperature + B11BrightnessTemperature) / 2
        cols = waterVapor.RasterXSize
        rows = waterVapor.RasterYSize
        cell_type = gdal.GDT_Float32
        driver_name = 'GTiff'
        projection = waterVapor.GetProjection()
        transform = waterVapor.GetGeoTransform()
#
        output_path = self.ui.outputLSTLine.text()
#
        l8_lst_swa_common_lib.save_nparray_as_raster(LSTArray,driver_name,cell_type,cols,rows,projection,transform,output_path)

        del waterVaporArray
        del B10BrightnessTemperature
        del B11BrightnessTemperature
        del LSE10Array
        del LSE11Array
        gc.collect()

    def prepareRawLandsat(self):
        """
        Get path to scenes from metadata and convert all to radiance
        """
        tempPath = os.path.dirname(os.path.abspath(__file__)) + '\\temp\\'
        metadataPath = self.ui.satTabMTLPathLine.text()
        mtl_dict = l8_lst_swa_common_lib.readBasicMetadata(metadataPath)
        metadataBasePath = os.path.dirname(metadataPath)
        #print 'step1'
        ### B4, B5, B10, B11 to radiance
        B4Radiance = l8_lst_swa_common_lib.Landsat8_DN_to_radiance(1,metadataBasePath + '/' + mtl_dict['mtl_band4'],4,metadataPath)
        B5Radiance = l8_lst_swa_common_lib.Landsat8_DN_to_radiance(1,metadataBasePath + '/' + mtl_dict['mtl_band5'],5,metadataPath)
        #print 'step2'

        B10BrightnessTemperature = l8_lst_swa_common_lib.Landsat8_simple_temperature(1,metadataBasePath + '/' + mtl_dict['mtl_band10'],10,metadataPath)
        B11BrightnessTemperature = l8_lst_swa_common_lib.Landsat8_simple_temperature(1,metadataBasePath + '/' + mtl_dict['mtl_band11'],11,metadataPath)
        #print 'step3'

        ### NDVI Array
        NDVIArray = (B5Radiance - B4Radiance) / (B5Radiance + B4Radiance)
        del B4Radiance
        del B5Radiance
        #print 'done'

        getLSEByNDVIVectorized = np.vectorize(l8_lst_swa_core.getLSEByNDVI)
        LSE10Array = getLSEByNDVIVectorized(NDVIArray, 10)
        LSE11Array = getLSEByNDVIVectorized(NDVIArray, 11)
        print 'done'
        return mtl_dict, B10BrightnessTemperature, B11BrightnessTemperature, LSE10Array, LSE11Array


    def run(self):
        if not self.ui.statusSatelliteCheckBox.isChecked():
            QtGui.QMessageBox.critical(None, "Error", 'Satellite data is not checked!')
            self.readyInterface()
            return
        if not self.ui.statusMeteoCheckBox.isChecked():
            QtGui.QMessageBox.critical(None, "Error", 'Meteorological data is not checked!')
            self.readyInterface()
            return
        if not self.ui.statusGroundCheckBox.isChecked():
            QtGui.QMessageBox.critical(None, "Error", 'Ground data is not checked!')
            self.readyInterface()
            return
        if not self.ui.statusOutputCheckBox.isChecked():
            QtGui.QMessageBox.critical(None, "Error", 'Output data is not checked!')
            self.readyInterface()
            return

        l8_lst_swa_common_lib.clearDir()
        self.getInputs()


        pass

    def cancel(self):
        """
        Close window by pressing "Cancel" button
        """
        #ABCCoefs = l8_lst_swa_core.getABCCoefsForB10B11()
        #KDCoefs = l8_lst_swa_core.getKDCoefsForB10B11()
        #print l8_lst_swa_core.getLSTWithSWAForPixel(ABCCoefs,KDCoefs,2.1,0.993,0.965,22.1+273.15,24.3+273.15)

        self.close()