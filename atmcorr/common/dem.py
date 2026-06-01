from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from osgeo import gdal

from .constants import DEFAULT_DEM_PATH

gdal.UseExceptions()


@dataclass(frozen=True)
class GeoBounds:
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


def mean_dem(bounds: GeoBounds, dem_path: str | Path = DEFAULT_DEM_PATH) -> float:
    """Return mean elevation in meters for a lon/lat bounding box."""
    dataset = gdal.Open(str(dem_path))
    if dataset is None:
        raise RuntimeError(f"Failed to open DEM file: {dem_path}")

    try:
        band = dataset.GetRasterBand(1)
        transform = dataset.GetGeoTransform()
        origin_x, pixel_width, _, origin_y, _, pixel_height = transform

        x1 = int((bounds.min_lon - origin_x) / pixel_width)
        x2 = int((bounds.max_lon - origin_x) / pixel_width)
        y1 = int((origin_y - bounds.max_lat) / abs(pixel_height))
        y2 = int((origin_y - bounds.min_lat) / abs(pixel_height))

        x_start = max(0, min(x1, x2))
        x_end = min(dataset.RasterXSize, max(x1, x2))
        y_start = max(0, min(y1, y2))
        y_end = min(dataset.RasterYSize, max(y1, y2))

        x_size = x_end - x_start
        y_size = y_end - y_start
        if x_size <= 0 or y_size <= 0:
            raise ValueError(f"DEM bounds do not intersect DEM extent: {bounds}")

        values = band.ReadAsArray(x_start, y_start, x_size, y_size)
        if values is None or values.size == 0:
            raise ValueError(f"DEM read returned no data for bounds: {bounds}")

        nodata = band.GetNoDataValue()
        if nodata is not None:
            values = values[values != nodata]
        if values.size == 0:
            raise ValueError(f"DEM region contains only nodata values: {bounds}")

        return float(np.mean(values))
    finally:
        dataset = None
