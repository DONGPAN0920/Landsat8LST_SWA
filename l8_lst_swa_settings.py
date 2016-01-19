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
import urllib2

from PyQt4.QtGui import QFileDialog

from ui import l8_lst_swa_settings_ui
from PyQt4 import QtGui, QtCore

import os
import re
import l8_lst_swa_main
import spacetrack_interface

class L8_lst_swaSettingsDlg(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = l8_lst_swa_settings_ui.Ui_Dialog()
        self.ui.setupUi(self)

        # Button's handlers
        self.connect(self.ui.applyButton, QtCore.SIGNAL("clicked()"), self.apply)
        self.connect(self.ui.MRTSwathBinDirButton, QtCore.SIGNAL("clicked()"), self.mrtBinBrowse)
        self.connect(self.ui.MRTSwathDataDirButton, QtCore.SIGNAL("clicked()"), self.mrtDataBrowse)
        self.connect(self.ui.downloadsDirButton, QtCore.SIGNAL("clicked()"), self.downloadDataBrowse)

        self.connect(self.ui.TLEAutoButton, QtCore.SIGNAL("clicked()"), self.autoTLE)


        #Refresh from file
        try:
            dirPath = os.path.dirname(os.path.abspath(__file__))
            # spacetrack
            spacetrack_opt = open(dirPath + '\\' +'spacetrack.dat','r')
            login = spacetrack_opt.readline()
            password = spacetrack_opt.readline()
            self.ui.SpacetrackLoginLine.setText(re.sub("^\s+|\n|\r|\s+$", '', login))
            self.ui.SpaceTrackPasswordLine.setText(re.sub("^\s+|\n|\r|\s+$", '', password))

            # mrt
            mrtswath_opt = open(dirPath + '\\' +'mrtswath.dat','r')
            mrt_bin = mrtswath_opt.readline()
            mrt_data = mrtswath_opt.readline()
            mrt_download = mrtswath_opt.readline()
            self.ui.MRTSwathBinDirLine.setText(re.sub("^\s+|\n|\r|\s+$", '', mrt_bin))
            self.ui.MRTSwathDataDirLine.setText(re.sub("^\s+|\n|\r|\s+$", '', mrt_data))
            self.ui.downloadsDirLine.setText(re.sub("^\s+|\n|\r|\s+$", '', mrt_download))

            # TLE
            tle_opt = open(dirPath + '\\' +'tle.tle','r')
            TLELine1 = tle_opt.readline()
            TLELine2 = tle_opt.readline()
            self.ui.TLELine1.setText(re.sub("^\s+|\n|\r|\s+$", '', TLELine1))
            self.ui.TLELine2.setText(re.sub("^\s+|\n|\r|\s+$", '', TLELine2))

        except:
            pass

    def mrtBinBrowse(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.ui.MRTSwathBinDirLine.setText(dir)

    def mrtDataBrowse(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.ui.MRTSwathDataDirLine.setText(dir)

    def downloadDataBrowse(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.ui.downloadsDirLine.setText(dir)

    def autoTLE(self):
        try:
            login = self.ui.SpacetrackLoginLine.text()
            password = self.ui.SpaceTrackPasswordLine.text()
        except:
            QtGui.QMessageBox.critical(None, "Error", 'Login and password are not set')
            return

        currentDate = l8_lst_swa_main.L8_lst_swaMainDlg.currentDate.split('.')

        userYear = int(currentDate[2])
        userMonth = int(currentDate[1])
        userDay = int(currentDate[0])
        satId = 25994

        try:
            tle1, tle2 = spacetrack_interface.get_spacetrack_tle_for_id_date(satId,userYear,userMonth,userDay,login,password)
        except (NameError):
            QtGui.QMessageBox.critical(None, "Error", 'Server is unavailable')
            return
        except (urllib2.HTTPError):
            QtGui.QMessageBox.critical(None, "Error", 'Invalid inputs. Check date.')
            return
        except:
            QtGui.QMessageBox.critical(None, "Error", 'Unable to recieve TLE')
            return

        self.ui.TLELine1.setText(tle1)
        self.ui.TLELine2.setText(tle2)

    def apply(self):
        try:
            dirPath = os.path.dirname(os.path.abspath(__file__))
            spacetrack_opt = open(dirPath + '\\' +'spacetrack.dat','w')
            mrtswath_opt = open(dirPath + '\\' +'mrtswath.dat','w')
            tle_opt = open(dirPath + '\\' +'tle.tle','w')

            spacetrack_opt.write(self.ui.SpacetrackLoginLine.text())
            spacetrack_opt.write('\n')
            spacetrack_opt.write(self.ui.SpaceTrackPasswordLine.text())
            spacetrack_opt.close()

            mrtswath_opt.write(self.ui.MRTSwathBinDirLine.text())
            mrtswath_opt.write('\n')
            mrtswath_opt.write(self.ui.MRTSwathDataDirLine.text())
            mrtswath_opt.write('\n')
            mrtswath_opt.write(self.ui.downloadsDirLine.text())
            mrtswath_opt.close()

            tle_opt.write(self.ui.TLELine1.text())
            tle_opt.write('\n')
            tle_opt.write(self.ui.TLELine2.text())
            tle_opt.close()
        except:
            pass

        self.close()