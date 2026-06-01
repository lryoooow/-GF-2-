#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : zhaoguanhua
@Email   : zhaogh@hdsxtech.com
@Time    : 2019/12/25 14:00
@File    : base.py
@Software: PyCharm
"""

import os
import numpy as np
from osgeo import gdal

gdal.UseExceptions()

def MeanDEM(pointUL, pointDR):
    '''
    璁＄畻褰卞儚鎵€鍦ㄥ尯鍩熺殑骞冲潎楂樼▼.
    '''
    script_path = os.path.split(os.path.realpath(__file__))[0]
    dem_path = os.path.join(script_path,"GMTED2km.tif")

    DEMIDataSet = gdal.Open(dem_path)
    if DEMIDataSet is None:
        raise RuntimeError("Failed to open DEM file: {}".format(dem_path))

    DEMBand = DEMIDataSet.GetRasterBand(1)
    geotransform = DEMIDataSet.GetGeoTransform()
    # DEM鍒嗚鲸鐜?    pixelWidth = geotransform[1]
    pixelHight = geotransform[5]

    # DEM璧峰鐐癸細宸︿笂瑙掞紝X锛氱粡搴︼紝Y锛氱含搴?    originX = geotransform[0]
    originY = geotransform[3]

    # 鐮旂┒鍖哄乏涓婅鍦―EM鐭╅樀涓殑浣嶇疆
    yoffset1 = int((originY - pointUL['lat']) / pixelWidth)
    xoffset1 = int((pointUL['lon'] - originX) / (-pixelHight))

    # 鐮旂┒鍖哄彸涓嬭鍦―EM鐭╅樀涓殑浣嶇疆
    yoffset2 = int((originY - pointDR['lat']) / pixelWidth)
    xoffset2 = int((pointDR['lon'] - originX) / (-pixelHight))

    # 鐮旂┒鍖虹煩闃佃鍒楁暟
    xx = xoffset2 - xoffset1
    yy = yoffset2 - yoffset1
    # 璇诲彇鐮旂┒鍖哄唴鐨勬暟鎹紝骞惰绠楅珮绋?    DEMRasterData = DEMBand.ReadAsArray(xoffset1, yoffset1, xx, yy)

    MeanAltitude = np.mean(DEMRasterData)
    return MeanAltitude

