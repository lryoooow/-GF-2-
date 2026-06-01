#! usr/bin/env python
# -*- coding:utf-8 -*-
# created by zhaoguanhua 2017/10/23

from osgeo import gdal
from osgeo import osr
import numpy as np

def getSRSPair(dataset):
    '''
    鑾峰緱缁欏畾鏁版嵁鐨勬姇褰卞弬鑰冪郴鍜屽湴鐞嗗弬鑰冪郴
    :param dataset: GDAL鍦扮悊鏁版嵁
    :return: 鎶曞奖鍙傝€冪郴鍜屽湴鐞嗗弬鑰冪郴
    '''
    prosrs = osr.SpatialReference()

    prosrs.ImportFromWkt(dataset.GetProjection())
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs

def geo2lonlat(dataset, x, y):
    '''
    灏嗘姇褰卞潗鏍囪浆涓虹粡绾害鍧愭爣锛堝叿浣撶殑鎶曞奖鍧愭爣绯荤敱缁欏畾鏁版嵁纭畾锛?    :param dataset: GDAL鍦扮悊鏁版嵁
    :param x: 鎶曞奖鍧愭爣x
    :param y: 鎶曞奖鍧愭爣y
    :return: 鎶曞奖鍧愭爣(x, y)瀵瑰簲鐨勭粡绾害鍧愭爣(lon, lat)
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]

def lonlat2geo(dataset, lon, lat):
    '''
    灏嗙粡绾害鍧愭爣杞负鎶曞奖鍧愭爣锛堝叿浣撶殑鎶曞奖鍧愭爣绯荤敱缁欏畾鏁版嵁纭畾锛?    :param dataset: GDAL鍦扮悊鏁版嵁
    :param lon: 鍦扮悊鍧愭爣lon缁忓害
    :param lat: 鍦扮悊鍧愭爣lat绾害
    :return: 缁忕含搴﹀潗鏍?lon, lat)瀵瑰簲鐨勬姇褰卞潗鏍?    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lon, lat)
    return coords[:2]

def imagexy2geo(dataset, row, col):
    '''
    鏍规嵁GDAL鐨勫叚鍙傛暟妯″瀷灏嗗奖鍍忓浘涓婂潗鏍囷紙琛屽垪鍙凤級杞负鎶曞奖鍧愭爣鎴栧湴鐞嗗潗鏍囷紙鏍规嵁鍏蜂綋鏁版嵁鐨勫潗鏍囩郴缁熻浆鎹級
    :param dataset: GDAL鍦扮悊鏁版嵁
    :param row: 鍍忕礌鐨勮鍙?    :param col: 鍍忕礌鐨勫垪鍙?    :return: 琛屽垪鍙?row, col)瀵瑰簲鐨勬姇褰卞潗鏍囨垨鍦扮悊鍧愭爣(x, y)
    '''
    trans = dataset.GetGeoTransform()
    px = trans[0] + row * trans[1] + col * trans[2]
    py = trans[3] + row * trans[4] + col * trans[5]
    return px, py

def geo2imagexy(dataset, x, y):
    '''
    鏍规嵁GDAL鐨勫叚 鍙傛暟妯″瀷灏嗙粰瀹氱殑鎶曞奖鎴栧湴鐞嗗潗鏍囪浆涓哄奖鍍忓浘涓婂潗鏍囷紙琛屽垪鍙凤級
    :param dataset: GDAL鍦扮悊鏁版嵁
    :param x: 鎶曞奖鎴栧湴鐞嗗潗鏍噚
    :param y: 鎶曞奖鎴栧湴鐞嗗潗鏍噛
    :return: 褰卞潗鏍囨垨鍦扮悊鍧愭爣(x, y)瀵瑰簲鐨勫奖鍍忓浘涓婅鍒楀彿(row, col)
    '''
    trans = dataset.GetGeoTransform()
    a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
    b = np.array([x - trans[0], y - trans[3]])
    return np.linalg.solve(a, b)  # 浣跨敤numpy鐨刲inalg.solve杩涜浜屽厓涓€娆℃柟绋嬬殑姹傝В

if __name__ == '__main__':
    gdal.AllRegister()
    dataset = gdal.Open('/Users/zhaoguanhua/2017/Project/Data/SurfaceReflectance/sentinel/15SUC/tiles/15/S/UC/2017/1/7/0/B02.tiff')
    print('鏁版嵁鎶曞奖锛?)
    print(dataset.GetProjection())
    print('鏁版嵁鐨勫ぇ灏忥紙琛岋紝鍒楋級锛?)
    print('(%s %s)' % (dataset.RasterYSize, dataset.RasterXSize))

    x = 300000
    y = 4300020
    lon = 122.47242
    lat = 52.51778
    row = 2399
    col = 3751

    print('鎶曞奖鍧愭爣 -> 缁忕含搴︼細')
    coords = geo2lonlat(dataset, x, y)
    print('(%s, %s)->(%s, %s)' % (x, y, coords[0], coords[1]))
    print('缁忕含搴?-> 鎶曞奖鍧愭爣锛?)
    coords = lonlat2geo(dataset, lon, lat)
    print('(%s, %s)->(%s, %s)' % (lon, lat, coords[0], coords[1]))

    print('鍥句笂鍧愭爣 -> 鎶曞奖鍧愭爣锛?)
    coords = imagexy2geo(dataset, row, col)
    print('(%s, %s)->(%s, %s)' % (row, col, coords[0], coords[1]))
    print('鎶曞奖鍧愭爣 -> 鍥句笂鍧愭爣锛?)
    coords = geo2imagexy(dataset, x, y)
    print('(%s, %s)->(%s, %s)' % (x, y, coords[0], coords[1]))





