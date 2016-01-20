from optparse import OptionParser
from pyorbital.orbital import Orbital
from pyorbital.tlefile import ChecksumError
import datetime
from PyQt4.QtCore import *
from qgis.core import *
from PyQt4.QtGui import QApplication

def create_orbital_track_shapefile_for_day (year, month, day, step_minutes, tle_line1, tle_line2, sat_name):
    try:
        orb = Orbital("N",tle_file=None,line1=tle_line1, line2=tle_line2)
    except:
        raise NameError

    try:
        year = int(year)
        month = int(month)
        day = int(day)
        step_minutes = float(step_minutes)
    except:
        raise TypeError

    trackLayerName = 'Track Layer (' + str(sat_name) + ': ' + str(year) + ':' + str(month) + ':' + str(day) + ')'
    trackLayer = QgsVectorLayer("Point", trackLayerName, "memory")
    trackLayer.setCrs(QgsCoordinateReferenceSystem(4326))
    trackLayerDataProvider = trackLayer.dataProvider()

    trackLayer.startEditing()

    trackLayerDataProvider.addAttributes( [ QgsField("ID", QVariant.Int),
                QgsField("TIME",  QVariant.String),
                QgsField("LAT", QVariant.Double),
                QgsField("LON", QVariant.Double)] )

    i = 0
    minutes = 0
    while minutes < 1440:
        QApplication.processEvents()
        utc_hour = int(minutes // 60)
        utc_minutes = int((minutes - (utc_hour*60)) // 1)
        utc_seconds = int(round((minutes - (utc_hour*60) - utc_minutes)*60))

        utc_string = str(utc_hour) + ':' + str(utc_minutes) + ':' + str(utc_seconds)

        utc_time = datetime.datetime(year,month,day,utc_hour,utc_minutes,utc_seconds)

        lon, lat, alt = orb.get_lonlatalt(utc_time)

        trackPoint = QgsFeature()
        trackPoint.setGeometry(QgsGeometry.fromPoint(QgsPoint(lon,lat)))
        trackPoint.setAttributes([i,utc_string,float(lat),float(lon)])

        trackLayerDataProvider.addFeatures ([trackPoint])

        i += 1
        minutes += step_minutes

    trackLayer.commitChanges()
    trackLayer.updateExtents()

    return trackLayer