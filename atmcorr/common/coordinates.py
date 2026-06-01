from __future__ import annotations

import numpy as np
from osgeo import osr


def get_srs_pair(dataset):
    projected = osr.SpatialReference()
    projected.ImportFromWkt(dataset.GetProjection())
    geographic = projected.CloneGeogCS()
    return projected, geographic


def geo_to_lonlat(dataset, x: float, y: float) -> tuple[float, float]:
    projected, geographic = get_srs_pair(dataset)
    transform = osr.CoordinateTransformation(projected, geographic)
    lon, lat, *_ = transform.TransformPoint(x, y)
    return lon, lat


def lonlat_to_geo(dataset, lon: float, lat: float) -> tuple[float, float]:
    projected, geographic = get_srs_pair(dataset)
    transform = osr.CoordinateTransformation(geographic, projected)
    x, y, *_ = transform.TransformPoint(lon, lat)
    return x, y


def imagexy_to_geo(dataset, row: float, col: float) -> tuple[float, float]:
    transform = dataset.GetGeoTransform()
    x = transform[0] + col * transform[1] + row * transform[2]
    y = transform[3] + col * transform[4] + row * transform[5]
    return x, y


def geo_to_imagexy(dataset, x: float, y: float) -> tuple[float, float]:
    transform = dataset.GetGeoTransform()
    matrix = np.array([[transform[1], transform[2]], [transform[4], transform[5]]])
    vector = np.array([x - transform[0], y - transform[3]])
    col, row = np.linalg.solve(matrix, vector)
    return row, col
