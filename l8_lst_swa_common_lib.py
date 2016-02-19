import re
from qgis.core import *

import tempfile
import errno
import exceptions
from osgeo import gdal
import numpy as np
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
import os
import glob

def clearDir (path = os.path.dirname(os.path.abspath(__file__)) + '\\temp\\'):
    #tempPath = os.path.dirname(os.path.abspath(__file__)) + '\\temp\\'
    for file in glob.glob(path + '*.*'):
        try:
            os.remove(file)
        except:
            pass

def isWritable(path):
    """
    Check if path is writable
    :param path: string; path to be checked
    :return: Boolean
    """
    try:
        testfile = tempfile.TemporaryFile(dir = path)
        testfile.close()
    except OSError as e:
        if e.errno == errno.EACCES:  # 13
            return False
        e.filename = path
        raise
    return True


def getLayerByName(vectorLayerName):
    """
    Return QgsVectorLayer by name from project layers
    :param vectorLayerName: string; QgsVectorLayer's name
    :return: QgsVectorLayer
    """
    layer = None
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.name() == vectorLayerName:
            layer = lyr
            break

    return layer

def saveVectorLayerToSHP(vectorLayer, shpFullPath):
    """
    Write given QgsVectorLayer to file system as shapefile
    :param vectorLayer: QgsVectorLayer;
    :param shpFullPath: string
    :return: 0 if everything is OK, else error codes
    """
    error = QgsVectorFileWriter.writeAsVectorFormat(vectorLayer, shpFullPath, "UTF-8", None, "ESRI Shapefile")
    return error

def getFeaturesAsList (vectorLayer):
    """
    Return all features of QgsVectorLayer a list (cause Qgis default is iterator)
    :param vectorLayer: QgsVectorLayer
    :return: list of features (QgsFeature)
    """
    features = vectorLayer.getFeatures()
    featuresList = []
    for feature in features:
        featuresList.append(feature)

    return featuresList



def reprojectVectorLayerToMemoryLayer (sourceCRS, destCRS, vectorLayer):
    """
    Generates new vector layer, each feature of which is reprojected from sourceCRS to destCRS
    Multigeometry for now is not supported
    :param sourceCRS: QgsCoordinateReferenceSystem (native for input vector layer)
    :param destCRS: QgsCoordinateReferenceSystem (destination, input layer will be reprojected to it)
    :param vectorLayer: QgsVectorLayer (to be reprojected)
    :return: QgsVectorLayer (reprojected) as memory layer; None if unsupported type of geometry
    """
    xform = QgsCoordinateTransform(sourceCRS, destCRS)

    if vectorLayer.wkbType() == QGis.WKBPolygon:
        memoryLayer = QgsVectorLayer('Polygon', 'New Layer', "memory")
        memoryLayer.setCrs(destCRS)
        memoryLayerDataProvider = memoryLayer.dataProvider()
        memoryLayer.startEditing()

        sourceFeatures = vectorLayer.getFeatures()

        for sourceFeature in sourceFeatures:
            destFeature = QgsFeature()
            destFeature.setAttributes(sourceFeature.attributes())

            destGeom = [[]]
            sourceGeom = sourceFeature.geometry().asPolygon()
            for coordinates in sourceGeom[0]:
                destX, destY = xform.transform(coordinates[0],coordinates[1])
                destGeom[0].append(QgsPoint(destX, destY))
            destFeature.setGeometry(QgsGeometry.fromPolygon(destGeom))

            memoryLayerDataProvider.addFeatures([destFeature])

        memoryLayer.commitChanges()
        memoryLayer.updateExtents()
        return memoryLayer


    if vectorLayer.wkbType() == QGis.WKBLineString:
        memoryLayer = QgsVectorLayer('Linestring', 'New Layer', "memory")
        memoryLayer.setCrs(destCRS)

        memoryLayerDataProvider = memoryLayer.dataProvider()
        memoryLayer.startEditing()

        sourceFeatures = vectorLayer.getFeatures()

        for sourceFeature in sourceFeatures:
            destFeature = QgsFeature()
            destFeature.setAttributes(sourceFeature.attributes())

            destGeom = []
            sourceGeom = sourceFeature.geometry().asPolyline()
            for coordinates in sourceGeom:
                destX, destY = xform.transform(coordinates[0],coordinates[1])
                destGeom.append(QgsPoint(destX, destY))
            destFeature.setGeometry(QgsGeometry.fromPolyline(destGeom))

            memoryLayerDataProvider.addFeatures([destFeature])

        memoryLayer.commitChanges()
        memoryLayer.updateExtents()
        return memoryLayer


    if vectorLayer.wkbType() == QGis.WKBPoint:
        memoryLayer = QgsVectorLayer('Point', 'New Layer', "memory")
        memoryLayer.setCrs(destCRS)

        memoryLayerDataProvider = memoryLayer.dataProvider()
        memoryLayer.startEditing()

        sourceFeatures = vectorLayer.getFeatures()

        for sourceFeature in sourceFeatures:
            destFeature = QgsFeature()
            destFeature.setAttributes(sourceFeature.attributes())

            sourceGeom = sourceFeature.geometry().asPoint()
            destX, destY = xform.transform(sourceGeom[0],sourceGeom[1])
            destGeom = QgsPoint (destX,destY)

            destFeature.setGeometry(QgsGeometry.fromPoint(destGeom))

            memoryLayerDataProvider.addFeatures([destFeature])

        memoryLayer.commitChanges()
        memoryLayer.updateExtents()
        return memoryLayer

    return None



def getRasterLayerExtent (inputRaster, outCRS = None):
    """
    Return raster layer extent as dict. Extent can be reprojected on fly is outCRS is defined
    :param inputRaster: QgsRasterLayer
    :param outCRS: output CRS if reprojection is needed
    :return: dict: {'xMax': 0, 'xMin': 0, 'yMax': 0, 'yMin': 0,}
    """
    extent = inputRaster.extent()
    if not outCRS:
        return {'xMax':extent.xMaximum(),'xMin':extent.xMinimum(),'yMax':extent.yMaximum(),'yMin':extent.yMinimum()}
    else:
        sourceCRS = inputRaster.crs()
        xform = QgsCoordinateTransform(sourceCRS, outCRS)
        xMaxOut, yMaxOut = xform.transform(extent.xMaximum(), extent.yMaximum())
        xMinOut, yMinOut = xform.transform(extent.xMinimum(), extent.yMinimum())
        return {'xMax':max([xMaxOut,xMinOut]),'xMin':min([xMaxOut,xMinOut]),'yMax':max([yMaxOut,yMinOut]),'yMin':min([yMaxOut,yMinOut])}



##### Landsat #####

def read_metadata_parameter (metadata_path, parameter):
    """
     Read metadata parameter from Landsat 8 MTL file
    :param metadata_path: string; path to ...MTL.txt file of landsat 8 data set
    :param parameter: string; full name of parameter, e.g. RADIANCE_MAXIMUM_BAND_4
    :return: string; value of parameter at metadata; Exception if requested parameter not exists
    """
    metadata_file = open (metadata_path,'r')
    for line in metadata_file:
        if line.find(parameter) <> -1:
            equal_symbol_entrance = line.find ('=')
            value = line [equal_symbol_entrance+1:].replace(' ','').replace('"','')
            return value
    raise exceptions.MetadataError ('Parameter ' + parameter + ' not found at metadata')

def save_nparray_as_raster (nparray, driver_name, cell_type, base_raster_XSize, base_raster_YSize, base_raster_projection, base_raster_transform, out_path):
    """
    Save NumPy nparray as raster via GDAL library methods
    :param nparray: input nparray
    :param driver_name: driver name, e.g. GeoTIff
    :param cell_type: type of cell, e.g. Float32
    :param base_raster_XSize: X-resolution of output raster
    :param base_raster_YSize: Y-resolution of output raster
    :param base_raster_projection: Geographic projection for output raster
    :param base_raster_transform: Geographic transformation type for output raster
    :param out_path: where output raster will be saved
    """
    cols = base_raster_XSize
    rows = base_raster_YSize
    bands = 1
    dt = cell_type
    driver = gdal.GetDriverByName(driver_name)
    out_data = driver.Create(out_path,cols,rows,bands,dt)
    out_data.SetProjection (base_raster_projection)
    out_data.SetGeoTransform (base_raster_transform)

    out_data.GetRasterBand(1).WriteArray (nparray)

def Landsat8_DN_to_radiance (mode, raster_path, channel_number, metadata_path, output_path = None):
    """
    Convert raw Landsat8 scene from DN to radiance
    :param mode: int; mode 0 - generate tiff; mode 1 - return np array
    :param raster_path: string; input raster path
    :param channel_number: int; number of channel to be processed
    :param metadata_path: string; path to metadata file
    :param output_path: string; path for output radiance file
    :return:
    """
    try:
        int(channel_number)
    except:
        raise NameError('Channel number is not correct')

    if (int(channel_number)) < 1 or (int(channel_number) > 11):
        raise NameError('Channel number is not correct')

    metadata_channel_rad_maximum_str = 'RADIANCE_MAXIMUM_BAND_' + str(channel_number)
    metadata_channel_rad_minimum_str = 'RADIANCE_MINIMUM_BAND_' + str(channel_number)

    metadata_channel_quantize_max_str = 'QUANTIZE_CAL_MAX_BAND_' + str(channel_number)
    metadata_channel_quantize_min_str = 'QUANTIZE_CAL_MIN_BAND_' + str(channel_number)

    rad_maximum = float(read_metadata_parameter(metadata_path, metadata_channel_rad_maximum_str))
    rad_minimum = float(read_metadata_parameter(metadata_path, metadata_channel_rad_minimum_str))
    quantize_maximum = float(read_metadata_parameter(metadata_path, metadata_channel_quantize_max_str))
    quantize_minimum = float(read_metadata_parameter(metadata_path, metadata_channel_quantize_min_str))

    #print raster_path.replace('/','\\')
    landsat_dn_band = gdal.Open(re.sub("^\s+|\n|\r|\s+$", '', raster_path))
    #print landsat_dn_band
    landsat_dn_band_array = np.array(landsat_dn_band.GetRasterBand(1).ReadAsArray().astype(np.float32))
    print 'a???'
    landsat_radiance_band_array = ((rad_maximum - rad_minimum)/(quantize_maximum - quantize_minimum))*(landsat_dn_band_array - quantize_minimum) + rad_minimum
    print 'b???'
    if mode == 0:
        # Write result
        cols = landsat_dn_band.RasterXSize
        rows = landsat_dn_band.RasterYSize
        cell_type = gdal.GDT_Float32
        driver_name = 'GTiff'
        projection = landsat_dn_band.GetProjection()
        transform = landsat_dn_band.GetGeoTransform()
        save_nparray_as_raster(landsat_radiance_band_array,driver_name,cell_type,cols,rows,projection,transform,output_path)
        del landsat_radiance_band_array
        return
    else:
        return landsat_radiance_band_array

def Landsat8_simple_temperature (mode, raster_path, channel_number, metadata_path, output_path=None, base_raster=None):
    # mode 0 - generate tiff
    # mode 1 - return np array

    """
    Return brigtness temperature for Landsat's 8 B10 or B11.
    :param mode: int; mode 0 - generate tiff; mode 1 - return np array
    :param raster_path: string; input raster path
    :param channel_number: int; number of channel to be processed (10 or 11)
    :param metadata_path: string; path to metadata file
    :param output_path: string; path for output brightness temperature file
    :param base_raster: base geotiff layer (needed if mode = 0)
    :return: string; path for output radiance file
    """
    try:
        int(channel_number)
    except:
        raise NameError('Channel number is not correct')

    if (channel_number < 10) or (channel_number > 11):
        raise NameError('Channel number is not correct')

    landsat_radiance_band_array = Landsat8_DN_to_radiance(1,raster_path,channel_number,metadata_path)
    K1_constant = float(read_metadata_parameter(metadata_path,'K1_CONSTANT_BAND_' + str(channel_number)))
    K2_constant = float(read_metadata_parameter(metadata_path,'K2_CONSTANT_BAND_' + str(channel_number)))

    landsat_temperature_array = (K2_constant / np.log((K1_constant/landsat_radiance_band_array)+1)) - 273.15
    del landsat_radiance_band_array
    if mode == 0:
        base_raster = gdal.Open(re.sub("^\s+|\n|\r|\s+$", '', raster_path))
        cols = base_raster.RasterXSize
        rows = base_raster.RasterYSize
        cell_type = gdal.GDT_Float32
        driver_name = 'GTiff'
        projection = base_raster.GetProjection()
        transform = base_raster.GetGeoTransform()
        save_nparray_as_raster(landsat_temperature_array,driver_name,cell_type,cols,rows,projection,transform,output_path)
        del landsat_temperature_array
    else:
        return landsat_temperature_array

def readBasicMetadata (metadataPath):
    """
    Read basic metadata parameters, needed for SWA
    :param metadataPath: string; path to metadata file
    :return: dict; all parameters as dict
    """
    mtl_band4 = read_metadata_parameter(metadataPath,'FILE_NAME_BAND_4')
    mtl_band5 = read_metadata_parameter(metadataPath,'FILE_NAME_BAND_5')
    mtl_band10 = read_metadata_parameter(metadataPath,'FILE_NAME_BAND_10')
    mtl_band11 = read_metadata_parameter(metadataPath,'FILE_NAME_BAND_11')
    mtl_radiance10_min = read_metadata_parameter(metadataPath,'RADIANCE_MINIMUM_BAND_10')
    mtl_radiance10_max = read_metadata_parameter(metadataPath,'RADIANCE_MAXIMUM_BAND_10')
    mtl_radiance11_min = read_metadata_parameter(metadataPath,'RADIANCE_MINIMUM_BAND_11')
    mtl_radiance11_max = read_metadata_parameter(metadataPath,'RADIANCE_MAXIMUM_BAND_11')
    mtl_radiance4_min = read_metadata_parameter(metadataPath,'RADIANCE_MINIMUM_BAND_4')
    mtl_radiance4_max = read_metadata_parameter(metadataPath,'RADIANCE_MAXIMUM_BAND_4')
    mtl_radiance5_min = read_metadata_parameter(metadataPath,'RADIANCE_MINIMUM_BAND_5')
    mtl_radiance5_max = read_metadata_parameter(metadataPath,'RADIANCE_MAXIMUM_BAND_5')
    mtl_dict = {'mtl_band4':mtl_band4,'mtl_band5':mtl_band5,'mtl_band10':mtl_band10,'mtl_band11':mtl_band11,
                'mtl_radiance10_min':mtl_radiance10_min, 'mtl_radiance11_min':mtl_radiance11_min,
                'mtl_radiance10_max':mtl_radiance10_max, 'mtl_radiance11_max':mtl_radiance11_max,
                'mtl_radiance4_min':mtl_radiance4_min,'mtl_radiance5_min':mtl_radiance5_min,
                'mtl_radiance4_max':mtl_radiance4_max,'mtl_radiance5_max':mtl_radiance5_max}
    return mtl_dict



##### Water wapor #####

def generateOneValueRasterQGisCalc (baseRaster, value, outputPath):
    """
    Generates raster with extent and resolution of baseRaster, each pixel is value.
    QgsRasterCalculator used
    :param baseRaster:
    :param value: output value
    :param outputPath: path for output file
    """
    entries = []
    rCalcObj = QgsRasterCalculatorEntry()
    rCalcObj.ref = 'rCalcObj@1'
    rCalcObj.raster = baseRaster
    rCalcObj.bandNumber = 1
    entries.append(rCalcObj)
    calc = QgsRasterCalculator(str(value), outputPath, 'GTiff',
                               baseRaster.extent(),
                               baseRaster.width(), baseRaster.height(), entries)
    calc.processCalculation()

#def generateObeValueRasterByArrayGdal (baseRasterArray, value):
    # mode 0 - generate tiff
    # mode 1 - return np array
    #oneValueArray = (baseRasterArray / baseRasterArray) * value
    #return oneValueArray

#def transform

def adjustRasterToBaseRaster (baseRaster, adjustingRaster, outputPath):
    entries = []
    rCalcObj = QgsRasterCalculatorEntry()
    rCalcObj.ref = 'rCalcObj@1'
    rCalcObj.raster = adjustingRaster
    rCalcObj.bandNumber = 1
    entries.append(rCalcObj)
    #print '---'
    #print baseRaster.extent()
    #print baseRaster.width()
    #print baseRaster.height()
    #print '---'
    calc = QgsRasterCalculator('rCalcObj@1', outputPath, 'GTiff',
                               baseRaster.extent(),
                               baseRaster.width(), baseRaster.height(), entries)
    #print 'calc'
    calc.processCalculation()