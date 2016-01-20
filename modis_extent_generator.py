from PyQt4.QtCore import QVariant
from qgis.core import *
import modis_track_generator
import l8_lst_swa_common_lib
import math
from PyQt4.QtGui import QApplication

def generateTPEDProjection(lat1, lon1, lat2, lon2):
    crs = QgsCoordinateReferenceSystem()
    projString = '+proj=tpeqd +lat_1=' + str(lat1) + ' +lon_1=' + str(lon1) + ' +lat_2=' + str(lat2) + ' +lon_2=' + str(
            lon2) + ' +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
    crs.createFromProj4(projString)
    return crs


def generateLineWithPointFeatures(trackPointFeatures, reproject=False, sourceCRS=None, destCRS=None):
    trackLineFeature = QgsFeature()
    trackLineGeometry = []
    for feature in trackPointFeatures:
        geom = feature.geometry().asPoint()
        if (reproject == True) and sourceCRS and destCRS:
            xform = QgsCoordinateTransform(sourceCRS, destCRS)
            x, y = xform.transform(geom[0], geom[1])
            trackLineGeometry.append(QgsPoint(x, y))
        else:
            trackLineGeometry.append(QgsPoint(geom[0], geom[1]))
    trackLineFeatureGeometry = QgsGeometry.fromPolyline(trackLineGeometry)
    trackLineFeature.setGeometry(trackLineFeatureGeometry)
    return trackLineFeature


def addVertexesToPolyPoints(polyPoints, vertexCount):
    i = 0
    newPolyPoints = []
    while i < len(polyPoints) - 1:
        # first point
        newPolyPoints.append(QgsPoint(polyPoints[i][0], polyPoints[i][1]))

        dx = polyPoints[i + 1][0] - polyPoints[i][0]
        dy = polyPoints[i + 1][1] - polyPoints[i][1]
        length = math.sqrt(dx * dx + dy * dy)
        step = (length * 1.0) / (vertexCount * 1.0 - 1)
        if dx == 0 and dy == 0:
            i += 1
            continue

        if dx == 0.0:
            if dy > 0:
                a = 0
            else:
                a = math.pi
        elif dy == 0.0:
            if dx > 0:
                a = math.pi / 2
            else:
                a = (math.pi / 2) * 3
        else:
            r = math.atan(math.fabs(dx) / math.fabs(dy))

        if dx > 0:
            if dy > 0:
                a = r
            elif dy < 0:
                a = math.pi - r
        elif dx < 0:
            if dy > 0:
                a = 2 * math.pi - r
            elif dy < 0:
                a = math.pi + r
        j = 1
        while j < vertexCount:
            nX = polyPoints[i][0] + step * j * math.sin(a)
            nY = polyPoints[i][1] + step * j * math.cos(a)
            newPoint = QgsPoint(nX, nY)
            newPolyPoints.append(newPoint)
            j += 1
        # last point
        newPolyPoints.append(QgsPoint(polyPoints[i + 1][0], polyPoints[i + 1][1]))
        i += 1
    return newPolyPoints


def reprojectPolyPoints(polyPoints, sourceCRS, destCRS):
    xform = QgsCoordinateTransform(sourceCRS, destCRS)
    newPolyPoints = []
    i = 0
    for point in polyPoints:
        try:
            x, y = xform.transform(point[0], point[1])
            newPolyPoints.append(QgsPoint(x, y))
        except:
            pass
    return newPolyPoints


def getLineABCCoefficientsByTwoPoints(x1, y1, x2, y2):
    A = (y1 - y2)
    B = (x2 - x1)
    C = (x1 * y2 - x2 * y1)
    return A, B, C


# returns needed dictionary index from list of dictionaries by key
def findDictIndexInList(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


def generateSceneExtentForTrackLine(TrackLineFeature, WIDTH, sourceCRS, destCRS, splitBool):
    CROSS_CONST = 200
    geom = TrackLineFeature.geometry().asPolyline()

    polyPoints = [QgsPoint(geom[0][0], geom[0][1] + WIDTH), QgsPoint(geom[1][0], geom[1][1] + WIDTH),
                  QgsPoint(geom[1][0], geom[1][1] - WIDTH), QgsPoint(geom[0][0], geom[0][1] - WIDTH),
                  QgsPoint(geom[0][0], geom[0][1] + WIDTH)]

    ### Block to split scenes intersects 180 longitude to multigeom
    ###############################################################
    if splitBool:
        WGSTestPoints = reprojectPolyPoints(
                [QgsPoint(geom[0][0], geom[0][1] + WIDTH), QgsPoint(geom[1][0], geom[1][1] + WIDTH),
                 QgsPoint(geom[1][0], geom[1][1] - WIDTH), QgsPoint(geom[0][0], geom[0][1] - WIDTH),
                 QgsPoint(geom[0][0], geom[0][1] + WIDTH)], sourceCRS, destCRS)

        crossBool = False
        crossNodes = []
        i = 0
        while i < len(WGSTestPoints) - 1:
            QApplication.processEvents()
            if math.fabs(WGSTestPoints[i][0] - WGSTestPoints[i + 1][0]) > CROSS_CONST:
                crossBool = True
            i += 1

        # print WGSTestPoints

    ###############################################################
    ### End block

    ###

    # add vertexes
    polyPointsWithVertexes = addVertexesToPolyPoints(polyPoints, 30)

    reprojectedPolyPointsWithVertexes = reprojectPolyPoints(polyPointsWithVertexes, sourceCRS, destCRS)

    ### Block to split scenes intersects 180 longitude to multigeom
    ###############################################################
    if splitBool:
        crossNodes = []
        if crossBool:
            i = 0

            while i < len(reprojectedPolyPointsWithVertexes) - 1:
                QApplication.processEvents()
                if math.fabs(reprojectedPolyPointsWithVertexes[i][0] - reprojectedPolyPointsWithVertexes[i+1][0]) > CROSS_CONST:
                    A, B, C = getLineABCCoefficientsByTwoPoints(reprojectedPolyPointsWithVertexes[i][0], reprojectedPolyPointsWithVertexes[i][1],
                                                                reprojectedPolyPointsWithVertexes[i + 1][0], reprojectedPolyPointsWithVertexes[i + 1][1])

                    if (reprojectedPolyPointsWithVertexes[i][0] - reprojectedPolyPointsWithVertexes[i+1][0]) > 0:
                        crossX = 179.999
                    else:
                        crossX = -179.999

                    try:
                        crossY = (-A * crossX - C) / B
                    except:
                        crossY = 0

                    try:
                        crossNodes.append({'i': i, 'x': crossX, 'y': crossY, 'x2': -crossX, 'y2': crossY})
                    except:
                        i+=1
                        continue

                i += 1

            if len(crossNodes) > 1:
                crossPolyPoints = []
                crossIds = []
                i = 0
                while i < len(reprojectedPolyPointsWithVertexes) - 1:
                    QApplication.processEvents()
                    crossPolyPoints.append(QgsPoint(reprojectedPolyPointsWithVertexes[i][0], reprojectedPolyPointsWithVertexes[i][1]))
                    if findDictIndexInList(crossNodes, 'i', i) != -1:
                        dictIndex = findDictIndexInList(crossNodes, 'i', i)
                        x = crossNodes[dictIndex]['x']
                        y = crossNodes[dictIndex]['y']
                        x2 = crossNodes[dictIndex]['x2']
                        y2 = crossNodes[dictIndex]['y2']
                        crossPolyPoints.append(QgsPoint(x, y))
                        crossIds.append(len(crossPolyPoints) - 1)
                        crossPolyPoints.append(QgsPoint(x2, y2))

                    crossPolyPoints.append(QgsPoint(reprojectedPolyPointsWithVertexes[i + 1][0], reprojectedPolyPointsWithVertexes[i + 1][1]))
                    i += 1

                i = 0
                part = 1
                crossFeaturePoints1 = []
                crossFeaturePoints2 = []
                while i < len(crossPolyPoints) - 1:
                    QApplication.processEvents()
                    if (part == 1):
                        if i in crossIds:
                            crossFeaturePoints1.append(QgsPoint(crossPolyPoints[i][0], crossPolyPoints[i][1]))
                            part = 2
                        else:
                            crossFeaturePoints1.append(QgsPoint(crossPolyPoints[i][0], crossPolyPoints[i][1]))
                    elif (part == 2):
                        if i in crossIds:
                            crossFeaturePoints2.append(QgsPoint(crossPolyPoints[i][0], crossPolyPoints[i][1]))
                            part = 1
                        else:
                            crossFeaturePoints2.append(QgsPoint(crossPolyPoints[i][0], crossPolyPoints[i][1]))

                    i += 1

                scene = QgsFeature()
                scene.setGeometry(QgsGeometry.fromMultiPolygon([[crossFeaturePoints1, crossFeaturePoints2]]))
                return scene

    ###############################################################
    ### End block

    scene = QgsFeature()
    scene.setGeometry(QgsGeometry.fromPolygon([reprojectedPolyPointsWithVertexes]))
    return scene


def generateScenesExtentLayerForDay(year, month, day, tle_line1, tle_line2, sat_name, splitBool):
    WIDTH = 1165000

    trackLayer = modis_track_generator.create_orbital_track_shapefile_for_day(year, month, day, 5, tle_line1, tle_line2,
                                                                            sat_name)
    trackFeatures = l8_lst_swa_common_lib.getFeaturesAsList(trackLayer)

    i = 0
    j = 0
    scenesExtentLayerName = 'Scene\'s extents (' + sat_name + ': ' + str(year) + ':' + str(month) + ':' + str(day) + ')'
    scenesExtentLayer = QgsVectorLayer("MultiPolygon", scenesExtentLayerName, "memory")
    scenesExtentLayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.PostgisCrsId))
    scenesExtentLayer.startEditing()
    scenesExtentLayerDataProvider = scenesExtentLayer.dataProvider()
    scenesExtentLayerDataProvider.addAttributes([QgsField("ID", QVariant.Int),
                                                 QgsField("TIME", QVariant.String)])

    while i < len(trackFeatures) - 2:
        j = 0
        trackPointsPack = []
        while j <= 1:
            QApplication.processEvents()
            trackPointsPack.append(trackFeatures[i])

            j += 1
            i += 1

        if i != len(trackFeatures):
            i -= 1

        # now have pack with 2 points
        WGS84 = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.PostgisCrsId)
        TPED = generateTPEDProjection(round(trackPointsPack[0].geometry().asPoint()[1], 3),
                                      round(trackPointsPack[0].geometry().asPoint()[0], 3),
                                      round(trackPointsPack[1].geometry().asPoint()[1], 3),
                                      round(trackPointsPack[1].geometry().asPoint()[0], 3))
        trackPackLine = generateLineWithPointFeatures(trackPointsPack, True, WGS84, TPED)
        scene = generateSceneExtentForTrackLine(trackPackLine, WIDTH, TPED, WGS84, splitBool)
        scene.setAttributes([i, trackFeatures[i-1]['TIME']])
        scenesExtentLayerDataProvider.addFeatures([scene])

    scenesExtentLayer.commitChanges()
    scenesExtentLayer.updateExtents()
    return scenesExtentLayer
