from __future__ import annotations

import glob
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from osgeo import gdal

from atmcorr.common.constants import DEFAULT_DEM_PATH, NODATA
from atmcorr.common.dem import mean_dem
from atmcorr.common.raster import (
    corrected_reflectance_block,
    create_output_like,
    iter_windows,
    progress,
    window_count,
)
from atmcorr.common.sixs import SixSOptions, correction_coefficients

from .calibration import gain_bias, resolve_calibration_year, wavelength
from .metadata import GFSceneMetadata, load_gf_metadata

gdal.UseExceptions()

MSS_IMAGE_PATTERNS = ("*MSS*.tif", "*MSS*.tiff", "*mss*.tif", "*mss*.tiff")
MSS_XML_PATTERNS = ("*MSS*.xml", "*mss*.xml")
MSS_RPB_PATTERNS = ("*MSS*.rpb", "*mss*.rpb")


@dataclass(frozen=True)
class GFSceneFiles:
    scene_dir: Path
    image_path: Path
    metadata_path: Path
    rpb_path: Path


@dataclass(frozen=True)
class GFProcessOptions:
    fallback_year: str = "2019"
    block_size: int = 2048
    output_dtype: str = "int16"
    image_type: str = "MSS"
    sixs: SixSOptions = SixSOptions()
    dem_path: Path = DEFAULT_DEM_PATH


def _first_match(patterns: tuple[str, ...], directory: Path) -> Path | None:
    matches: list[str] = []
    for pattern in patterns:
        matches.extend(glob.glob(str(directory / pattern)))
    unique = sorted(set(matches))
    return Path(unique[0]) if unique else None


def find_gf_scenes(input_path: str | Path) -> list[Path]:
    path = Path(input_path)
    if not path.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {path}")
    if _first_match(MSS_IMAGE_PATTERNS, path):
        return [path]

    scenes = []
    for child in sorted(path.iterdir()):
        if child.is_dir() and child.name.upper().startswith("GF"):
            if _first_match(MSS_IMAGE_PATTERNS, child):
                scenes.append(child)
    return scenes


def locate_scene_files(scene_dir: str | Path) -> GFSceneFiles:
    directory = Path(scene_dir)
    image_path = _first_match(MSS_IMAGE_PATTERNS, directory)
    if image_path is None:
        raise FileNotFoundError(f"No MSS image found in {directory}")

    stem = image_path.stem
    metadata_path = _first_match((f"{stem}.xml", *MSS_XML_PATTERNS), directory)
    rpb_path = _first_match((f"{stem}.rpb", *MSS_RPB_PATTERNS), directory)
    if metadata_path is None:
        raise FileNotFoundError(f"No MSS metadata XML found in {directory}")
    if rpb_path is None:
        raise FileNotFoundError(f"No MSS RPB file found in {directory}")

    return GFSceneFiles(directory, image_path, metadata_path, rpb_path)


def output_scene_dir(output_root: str | Path, scene_dir: Path) -> tuple[Path, str]:
    scene_name = scene_dir.name
    directory = Path(output_root) / scene_name
    directory.mkdir(parents=True, exist_ok=True)
    return directory, scene_name


def _band_coefficients(
    band_id: int,
    metadata: GFSceneMetadata,
    config: dict,
    calibration_year: str,
    target_altitude_km: float,
    options: GFProcessOptions,
) -> tuple[float, float, float, float, float]:
    gain, bias = gain_bias(
        config,
        metadata.satellite_id,
        metadata.sensor_id,
        calibration_year,
        options.image_type,
        band_id,
    )
    coef_a, coef_b, coef_c = correction_coefficients(
        metadata.sixs_geometry(),
        target_altitude_km,
        wavelength(config, metadata.satellite_id, metadata.sensor_id, band_id),
        options.sixs,
    )
    return gain, bias, coef_a, coef_b, coef_c


def process_scene(
    scene_dir: str | Path,
    output_root: str | Path,
    config: dict,
    options: GFProcessOptions,
) -> Path:
    files = locate_scene_files(scene_dir)
    metadata = load_gf_metadata(files.metadata_path)
    calibration_year = resolve_calibration_year(
        config,
        metadata.satellite_id,
        metadata.sensor_id,
        metadata.year,
        options.fallback_year,
    )

    destination, scene_name = output_scene_dir(output_root, files.scene_dir)
    for source in (files.metadata_path, files.rpb_path):
        shutil.copy2(source, destination / source.name)

    dataset = gdal.Open(str(files.image_path))
    if dataset is None:
        raise RuntimeError(f"Failed to open image: {files.image_path}")
    if dataset.RasterCount < 4:
        raise RuntimeError(f"Expected at least 4 MSS bands: {files.image_path}")

    output_path = destination / f"{scene_name}.tiff"
    output = create_output_like(dataset, output_path, 4, options.output_dtype)
    target_altitude_km = mean_dem(metadata.bounds, options.dem_path) * 0.001

    print(f"Scene: {files.scene_dir}")
    print(f"Image: {files.image_path}")
    print(
        "Sensor: {}/{}; image year: {}; calibration year: {}; DEM: {:.3f} km".format(
            metadata.satellite_id,
            metadata.sensor_id,
            metadata.year,
            calibration_year,
            target_altitude_km,
        )
    )

    total_windows = window_count(dataset.RasterXSize, dataset.RasterYSize, options.block_size)
    try:
        for band_id in range(1, 5):
            read_band = dataset.GetRasterBand(band_id)
            out_band = output.GetRasterBand(band_id)
            out_band.SetNoDataValue(NODATA)

            coefficients = _band_coefficients(
                band_id,
                metadata,
                config,
                calibration_year,
                target_altitude_km,
                options,
            )

            valid_pixels = 0
            clipped_pixels = 0
            print(f"Processing band {band_id}")
            with progress(total_windows, f"band {band_id}") as pbar:
                for x_offset, y_offset, x_size, y_size in iter_windows(
                    dataset.RasterXSize, dataset.RasterYSize, options.block_size
                ):
                    image = read_band.ReadAsArray(x_offset, y_offset, x_size, y_size)
                    corrected, stats = corrected_reflectance_block(
                        image,
                        *coefficients,
                        output_dtype=options.output_dtype,
                    )
                    out_band.WriteArray(corrected, x_offset, y_offset)
                    valid_pixels += stats.valid_pixels
                    clipped_pixels += stats.clipped_pixels
                    pbar.update(1)

            out_band.FlushCache()
            print(
                f"Band {band_id} done: valid_pixels={valid_pixels}, "
                f"clipped_pixels={clipped_pixels}"
            )
    finally:
        output.FlushCache()
        output = None
        dataset = None

    return output_path


def process_input(
    input_dir: str | Path,
    output_dir: str | Path,
    config: dict,
    options: GFProcessOptions,
) -> list[Path]:
    scenes = find_gf_scenes(input_dir)
    if not scenes:
        raise FileNotFoundError(f"No GF MSS scene directories found in {input_dir}")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return [process_scene(scene, output_dir, config, options) for scene in scenes]
