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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from l8_lst_swa_main import L8_lst_swaMainDlg
from l8_lst_swa_about import L8_lst_swaAboutDlg
import os

class L8_lst_swa:

    def __init__(self,iface):
        self.iface=iface
        self.dlg = L8_lst_swaMainDlg()

    def initGui(self):

        dirPath = os.path.dirname(os.path.abspath(__file__))
        self.action = QAction(u"Landsat 8 LST Retriever (SWA)", self.iface.mainWindow())
        self.action.setIcon(QIcon(dirPath + "/icon.png"))
        self.iface.addPluginToRasterMenu(u"Landsat 8 LST Retriever (SWA)",self.action)
        self.action.setStatusTip(u"Landsat 8 LST Retriever (SWA)")
        self.iface.addRasterToolBarIcon(self.action)
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        self.aboutAction = QAction(u"About", self.iface.mainWindow())
        QObject.connect(self.aboutAction, SIGNAL("triggered()"), self.about)
        self.iface.addPluginToRasterMenu(u"Landsat 8 LST Retriever (SWA)", self.aboutAction)

    def unload(self):
        self.iface.removeRasterToolBarIcon(self.action)
        self.iface.removePluginRasterMenu(u"Landsat 8 LST Retriever (SWA)",self.action)

        self.iface.removePluginRasterMenu(u"Landsat 8 LST Retriever (SWA)",self.aboutAction)

    def run(self):
        self.L8_lst_swaMainDlg = L8_lst_swaMainDlg()
        self.L8_lst_swaMainDlg.show()

    def about(self):
        self.L8_lst_swaAboutDlg = L8_lst_swaAboutDlg()
        self.L8_lst_swaAboutDlg.show()