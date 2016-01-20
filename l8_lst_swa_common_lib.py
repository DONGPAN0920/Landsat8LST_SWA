from qgis.core import *

import tempfile
import errno

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