from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from osgeo import gdal
from tqdm import tqdm

from .constants import NODATA, REFLECTANCE_SCALE

gdal.UseExceptions()


GDAL_DTYPES = {
    "int16": gdal.GDT_Int16,
    "int32": gdal.GDT_Int32,
    "float32": gdal.GDT_Float32,
}

NUMPY_DTYPES = {
    "int16": np.int16,
    "int32": np.int32,
    "float32": np.float32,
}


@dataclass
class RasterStats:
    valid_pixels: int = 0
    clipped_pixels: int = 0


def create_output_like(source, output_path, band_count: int, output_dtype: str):
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(
        str(output_path),
        source.RasterXSize,
        source.RasterYSize,
        band_count,
        GDAL_DTYPES[output_dtype],
    )
    if dataset is None:
        raise RuntimeError(f"Failed to create output GeoTIFF: {output_path}")
    dataset.SetGeoTransform(source.GetGeoTransform())
    dataset.SetProjection(source.GetProjection())
    return dataset


def corrected_reflectance_block(
    image: np.ndarray,
    gain: float,
    bias: float,
    coef_a: float,
    coef_b: float,
    coef_c: float,
    output_dtype: str,
) -> tuple[np.ndarray, RasterStats]:
    mask = image > 0
    work = np.full(image.shape, NODATA, dtype=np.float32)
    np.multiply(image, gain, out=work, where=mask, casting="unsafe")
    np.add(work, bias, out=work, where=mask)
    np.multiply(work, coef_a, out=work, where=mask)
    np.subtract(work, coef_b, out=work, where=mask)

    valid = mask & np.isfinite(work)
    work[valid] = (work[valid] / (1.0 + work[valid] * coef_c)) * REFLECTANCE_SCALE

    stats = RasterStats(valid_pixels=int(np.count_nonzero(valid)))
    if output_dtype == "float32":
        output = np.full(image.shape, NODATA, dtype=np.float32)
        output[valid] = work[valid]
        return output, stats

    dtype = NUMPY_DTYPES[output_dtype]
    min_value = np.iinfo(dtype).min
    max_value = np.iinfo(dtype).max
    rounded = np.rint(work[valid])
    stats.clipped_pixels = int(np.count_nonzero((rounded < min_value) | (rounded > max_value)))

    output = np.full(image.shape, NODATA, dtype=dtype)
    output[valid] = np.clip(rounded, min_value, max_value).astype(dtype)
    return output, stats


def iter_windows(cols: int, rows: int, block_size: int):
    for y_offset in range(0, rows, block_size):
        y_size = min(block_size, rows - y_offset)
        for x_offset in range(0, cols, block_size):
            x_size = min(block_size, cols - x_offset)
            yield x_offset, y_offset, x_size, y_size


def window_count(cols: int, rows: int, block_size: int) -> int:
    return math.ceil(cols / block_size) * math.ceil(rows / block_size)


def progress(total: int, label: str):
    return tqdm(total=total, desc=label, mininterval=10)
