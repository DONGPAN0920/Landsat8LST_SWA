from qgis.core import *

import tempfile
import errno
import exceptions
from osgeo import gdal
import numpy as np
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

def isWritable(path):
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
    layer = None
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.name() == vectorLayerName:
            layer = lyr
            break

    return layer

def saveVectorLayerToSHP(vectorLayer, shpFullPath):
    error = QgsVectorFileWriter.writeAsVectorFormat(vectorLayer, shpFullPath, "UTF-8", None, "ESRI Shapefile")
    return error

def getFeaturesAsList (vectorLayer):
    features = vectorLayer.getFeatures()
    featuresList = []
    for feature in features:
        featuresList.append(feature)

    return featuresList



def reprojectVectorLayerToMemoryLayer (sourceCRS, destCRS, vectorLayer):
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
    extent = inputRaster.extent()
    if not outCRS:
        return {'xMax':extent.xMaximum(),'xMin':extent.xMinimum(),'yMax':extent.yMaximum(),'yMin':extent.yMinimum()}
    else:
        sourceCRS = inputRaster.crs()
        xform = QgsCoordinateTransform(sourceCRS, outCRS)
        xMaxOut, yMaxOut = xform.transform(extent.xMaximum(), extent.yMaximum())
        xMinOut, yMinOut = xform.transform(extent.xMinimum(), extent.yMinimum())
        return {'xMax':max([xMaxOut,xMinOut]),'xMin':min([xMaxOut,xMinOut]),'yMax':max([yMaxOut,yMinOut]),'yMin':min([yMaxOut,yMinOut])}



##### Landsat

def read_metadata_parameter (metadata_path, parameter):
    # Read metadata parameter from Landsat 8 MTL file
    metadata_file = open (metadata_path,'r')
    for line in metadata_file:
        if line.find(parameter) <> -1:
            equal_symbol_entrance = line.find ('=')
            value = line [equal_symbol_entrance+1:].replace(' ','').replace('"','')
            return value
    raise exceptions.MetadataError ('Parameter ' + parameter + ' not found at metadata')

def save_nparray_as_raster (nparray, driver_name, cell_type, base_raster_XSize, base_raster_YSize, base_raster_projection, base_raster_transform, out_path):
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
    # mode 0 - generate tiff
    # mode 1 - return np array

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

    landsat_dn_band = gdal.Open(raster_path)

    landsat_dn_band_array = np.array(landsat_dn_band.GetRasterBand(1).ReadAsArray().astype(np.float32))

    landsat_radiance_band_array = ((rad_maximum - rad_minimum)/(quantize_maximum - quantize_minimum))*(landsat_dn_band_array - quantize_minimum) + rad_minimum

    if mode == 0:
        # Write result
        cols = landsat_dn_band.RasterXSize
        rows = landsat_dn_band.RasterYSize
        cell_type = gdal.GDT_Float32
        driver_name = 'GTiff'
        projection = landsat_dn_band.GetProjection()
        transform = landsat_dn_band.GetGeoTransform()
        save_nparray_as_raster(landsat_radiance_band_array,driver_name,cell_type,cols,rows,projection,transform,output_path)
        return
        #return {"cols":cols,"rows":rows,"cell_type":cell_type,"driver_name":driver_name,"projection":projection,"transform":transform}
    else:
        return landsat_radiance_band_array

def Landsat8_simple_temperature (mode, raster_path, channel_number, metadata_path, output_path=None, base_raster=None):
    # mode 0 - generate tiff
    # mode 1 - return np array

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

    if mode == 0:
        base_raster = gdal.Open(raster_path)
        cols = base_raster.RasterXSize
        rows = base_raster.RasterYSize
        cell_type = gdal.GDT_Float32
        driver_name = 'GTiff'
        projection = base_raster.GetProjection()
        transform = base_raster.GetGeoTransform()
        save_nparray_as_raster(landsat_radiance_band_array,driver_name,cell_type,cols,rows,projection,transform,output_path)
    else:
        return landsat_temperature_array

def readBasicMetadata (metadataPath):
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



### Water wapor

def generateOneValueRasterQGisCalc (baseRaster, value, outputPath):
    # Generates raster with extent and resolution of baseRaster, each pixel is value
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

def generateObeValueRasterByArrayGdal (baseRasterArray, value):
    # mode 0 - generate tiff
    # mode 1 - return np array
    oneValueArray = (baseRasterArray / baseRasterArray) * value
    return oneValueArray

#def transform