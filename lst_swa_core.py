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
import math


def getT10T11FromWaterWaporContent (waterWaporContent):
    """
    Returns water wapor content by cubic regression
    :param waterWaporContent: float; water wapor content
    :return: dict;
    """
    T10 = 0.9570356 - 0.0277340*waterWaporContent - 0.0333734*waterWaporContent*waterWaporContent +\
          0.0028800 * waterWaporContent * waterWaporContent * waterWaporContent
    T11 = 0.9456728 - 0.0857755 * waterWaporContent - 0.0290912 * waterWaporContent * waterWaporContent +\
          0.0032169 * waterWaporContent * waterWaporContent * waterWaporContent
    return {"T10":T10, "T11": T11}

def getABCCoefsForB10B11():
    """
    Returns quadratic function coefficients a b c for B10 and B11
    :return: dict;
    """
    a10 = 0.0006678
    b10 = -0.2333226
    c10 = 21.1666266

    a11 = 0.0006188
    b11 = -0.1990475
    c11 = 16.7224278

    return {"a10":a10,"b10":b10,"c10":c10,"a11":a11,"b11":b11,"c11":c11}

def getKDCoefsForB10B11():
    k10 = 0.1312942
    d10 = -26.7808503

    k11 = 0.1387986
    d11 = -27.7043284
    return {"k10":k10,"d10":d10,"k11":k11,"d11":d11}

def getLSEByNDVI(NDVI):
    if NDVI > 0.5:
        LSE10 = 0.984
        LSE11 = 0.980
    elif (NDVI > 0.2) and (NDVI <= 0.5):
        LSE10 = 0.959
        LSE11 = 0.962
    elif (NDVI > 0.0) and (NDVI <= 0.2):
        LSE10 = 0.964
        LSE11 = 0.970
    elif NDVI < 0:
        LSE10 = 0.991
        LSE11 = 0.986
    return {"LSE10":LSE10, "LSE11":LSE11}

def getBnTByPlanckLaw (BrigtnessTemperature, waveLength):
    k = 1.3806485279 * (10**(-23)) # Boltzman constant
    h = 6.62607004081 * (10**(-34)) # Planck constant
    c = 299792458 # Speed of light
    BnT = (2 * h * c * c * waveLength * waveLength *waveLength) / (math.pow(math.e,(h*c*waveLength/k*BrigtnessTemperature))-1)
    return BnT

def getLSTWithSWAForPixel (ABCCoefs, KDCoefs, T10, T11, LSE10, LSE11, B10, B11):

    n10 = 10.9
    n11 = 12.0

    A10 = LSE10 * T10 * ABCCoefs["a10"]
    B10 = LSE10 * T10 * ABCCoefs["b10"]
    C10 = (1 - T10) * (1+(1-LSE10)*T10)*KDCoefs["k10"]

    B10T = getBnTByPlanckLaw(B10,n10)
    D10 = LSE10 * T10 * ABCCoefs["c10"] + (1-T10)*(1+(1-LSE10)*T10)*KDCoefs["d10"] - B10T

    A11 = LSE11 * T11 * ABCCoefs["a11"]
    B11 = LSE11 * T11 * ABCCoefs["b11"]
    C11 = (1 - T11) * (1+(1-LSE11)*T11)*KDCoefs["k11"]

    B11T = getBnTByPlanckLaw(B11,n11)
    D11 = LSE11 * T11 * ABCCoefs["c11"] + (1-T11)*(1+(1-LSE11)*T11)*KDCoefs["d11"] - B11T

    LST_up = ( (C10*B11-C11*B10) + math.sqrt( ((C10*B11-C11*B10)*(C10*B11-C11*B10)) - 4*(C11*A10-C10*A11)*(C11*D10-C10*D11) ) )
    LST_down = ( 2*(C11*A10 - C10*A11) )
    LST = LST_up / LST_down

    return LST