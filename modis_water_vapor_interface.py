# coding=utf-8
from PyQt4.QtGui import QApplication

import modis_extent_generator
from qgis.core import *
import l8_lst_swa_common_lib
import processing
import datetime
from urllib2 import urlopen
from ftplib import FTP
import shutil
from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest


def getWaterVaporForGivenRaster (inputRaster, year, month, day, outputPath,tle1,tle2,processLabel, tempDir):

    """
    Find needed MOD09 file for raster (e.g. Landsat scene) and download everything needed from NASA FTP'
    Then cut MOD09 by input raster and fix resolition.
    :param inputRaster: raster, for which's extent MOD09 will be searched
    :param year: year of aquisition
    :param month: month of aquisition
    :param day: day of aquisition
    :param outputPath: path, where final Water Vapor grid will be saved
    :param tle1: TLE line 1
    :param tle2: TLE line 2
    :param processLabel: qt label from interface to show status of progress
    :param tempDir: temporary directory where files will be downloaded
    :return: 1 or error code
    """
    processLabel.setText('Calculating TERRA track for day')
    QApplication.processEvents()

    scenesExtent = modis_extent_generator.generateScenesExtentLayerForDay(year,month,day,tle1,tle2,'Terra', True)

    processLabel.setText('Searching suitable scene for raster')
    QApplication.processEvents()
    WGS84 = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.PostgisCrsId)
    rasterExtent = l8_lst_swa_common_lib.getRasterLayerExtent(inputRaster, WGS84)
    rasterExtentGeom = [[QgsPoint(rasterExtent['xMin'],rasterExtent['yMin']),
                         QgsPoint(rasterExtent['xMin'],rasterExtent['yMax']),
                         QgsPoint(rasterExtent['xMax'],rasterExtent['yMax']),
                         QgsPoint(rasterExtent['xMax'],rasterExtent['yMin'])]]

    rasterMaskLayer = QgsVectorLayer("Polygon", 'Raster mask', "memory")
    rasterMaskLayerDP = rasterMaskLayer.dataProvider()
    rasterMaskLayer.startEditing()
    maskFeature = QgsFeature()
    maskFeature.setGeometry(QgsGeometry.fromPolygon(rasterExtentGeom))
    rasterMaskLayerDP.addFeatures([maskFeature])
    rasterMaskLayer.commitChanges()
    rasterMaskLayer.updateExtents()
    QgsMapLayerRegistry.instance().addMapLayer(rasterMaskLayer)
    QgsMapLayerRegistry.instance().addMapLayer(scenesExtent)
    try:
        processing.runalg('qgis:selectbylocation',scenesExtent,rasterMaskLayer,u'contains',0)
    except:
        raise


    containingScene = scenesExtent.selectedFeatures()[0]
    # Suitable scene time
    containingSceneTime = str(containingScene[1]).split(':')[0]+str(containingScene[1]).split(':')[1]

    processLabel.setText('Downloading MOD03...')
    QApplication.processEvents()

    MOD03 = downloadMODL2ForGivenDateAndTime(year,month,day,containingSceneTime,'MOD03',tempDir+'\\MOD03A.'+str(year)+str(month)+str(day)+'.'+str(containingSceneTime)+'.hdf')
    if MOD03 != 1:
        return MOD03

    processLabel.setText('Downloading MOD09...')
    QApplication.processEvents()

    MOD09 = downloadMODL2ForGivenDateAndTime(year,month,day,containingSceneTime,'MOD09',tempDir+'\\MOD09A.'+str(year)+str(month)+str(day)+'.'+str(containingSceneTime)+'.hdf')
    if MOD09 != 1:
        return MOD09


    QgsMapLayerRegistry.instance().removeMapLayer(rasterMaskLayer.id())
    QgsMapLayerRegistry.instance().removeMapLayer(scenesExtent.id())
    ### TO BE CONTINUED


def downloadMODL2ForGivenDateAndTime(year, month, day, time, product, rasterFullPath):
    """
    Downloads MODIS L2 product for given date. If success returns 1. Else error code from 2 to 6
    :param year: year of aquisition
    :param month: month of aquisition
    :param day:  day of aquisition
    :param time: time if format hhmm ( 0845 )
    :param product: Product code. MOD09, MOD03 etc.
    :param rasterLayerFullPath: path, where to download
    :return: 1 or error code
    """
    currentDate = datetime.date(year,month,day)
    currentDayOfYear = currentDate.timetuple().tm_yday
    currentDayOfYear = '0'*(3-len(str(currentDayOfYear))) + str(currentDayOfYear)

    try:
        ftp = FTP('ladsweb.nascom.nasa.gov') # MODIS NASA FTP
        ftp.login()
    except:
        return 2  # Bad connection

    try:
        ftp.cwd('allData/6/'+product+'/')
        ftp.cwd(str(year))
        ftp.cwd(str(currentDayOfYear))
    except:
        return 3  # Date is unavailable

    pathString = 'ftp://ladsweb.nascom.nasa.gov/allData/6/' + product + '/' + str(year) + '/' +\
                 str(currentDayOfYear) + '/'

    try:
        files = ftp.nlst()
    except:
        return 4  # File list is not available

    timestamp = str(year) + str(currentDayOfYear) + '.' + str(time)
    fileFlag = False
    for file in files:
        if (file[-3:] == 'hdf') and (file.find(timestamp) != -1):
            fileFlag = True
            pathString += file
            try:
                req = urlopen(pathString)
                dist = open(rasterFullPath, 'wb')
                shutil.copyfileobj(req, dist)
                dist.close()
            except:
                return 5  # Cannot download file

    if not fileFlag:
        return 6 # No needed file

    return 1

