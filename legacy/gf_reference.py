#! usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import glob
import json
import math
import os
import shutil
import sys
import time
import xml.dom.minidom

import numpy as np
from osgeo import gdal
from Py6S import *
from tqdm import tqdm

from base import MeanDEM


DEFAULT_CALIBRATION_FALLBACK_YEAR = "2019"

gdal.UseExceptions()


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="Atmospheric correction for GF multispectral imagery."
    )
    parser.add_argument("--Input_dir", type=str, required=True, help="GF scene directory or parent directory")
    parser.add_argument("--Output_dir", type=str, required=True, help="Output directory")
    parser.add_argument(
        "--Fallback_year",
        type=str,
        default=DEFAULT_CALIBRATION_FALLBACK_YEAR,
        help="Calibration year to use when the image year is missing from the parameter table.",
    )
    return parser.parse_args(argv)


def _first_match(patterns):
    matches = []
    for pattern in patterns:
        matches.extend(glob.glob(pattern))
    matches = sorted(set(matches))
    return matches[0] if matches else None


def find_gf_scenes(input_path):
    if not os.path.isdir(input_path):
        raise FileNotFoundError("Input_dir is not a directory: {}".format(input_path))

    if _first_match(
        [
            os.path.join(input_path, "*MSS*.tif"),
            os.path.join(input_path, "*MSS*.tiff"),
            os.path.join(input_path, "*mss*.tif"),
            os.path.join(input_path, "*mss*.tiff"),
        ]
    ):
        return [input_path]

    scenes = []
    for child in sorted(os.listdir(input_path)):
        child_path = os.path.join(input_path, child)
        if os.path.isdir(child_path) and child.upper().startswith("GF"):
            if _first_match(
                [
                    os.path.join(child_path, "*MSS*.tif"),
                    os.path.join(child_path, "*MSS*.tiff"),
                    os.path.join(child_path, "*mss*.tif"),
                    os.path.join(child_path, "*mss*.tiff"),
                ]
            ):
                scenes.append(child_path)
    return scenes


def load_scene_metadata(metadata_path):
    dom = xml.dom.minidom.parse(metadata_path)

    def text(tag):
        nodes = dom.getElementsByTagName(tag)
        if not nodes or nodes[0].firstChild is None:
            raise ValueError("Missing metadata tag '{}' in {}".format(tag, metadata_path))
        return nodes[0].firstChild.data.strip()

    center_time = text("CenterTime")
    return {
        "dom": dom,
        "satellite_id": text("SatelliteID"),
        "sensor_id": text("SensorID"),
        "year": center_time.split(" ")[0].split("-")[0],
    }


def resolve_calibration_year(config, satellite_id, sensor_id, year, fallback_year):
    sensor_config = config["Parameter"][satellite_id][sensor_id]
    if year in sensor_config:
        return year

    if fallback_year in sensor_config:
        print(
            "WARNING: calibration parameters for {}/{}/{} are missing; "
            "using {} for smoke testing only.".format(
                satellite_id, sensor_id, year, fallback_year
            )
        )
        return fallback_year

    available_years = sorted(k for k in sensor_config.keys() if k.isdigit())
    raise KeyError(
        "No calibration parameters for {}/{}/{}. Available years: {}".format(
            satellite_id, sensor_id, year, ", ".join(available_years)
        )
    )


def locate_mss_scene_files(scene_dir):
    image_path = _first_match(
        [
            os.path.join(scene_dir, "*MSS*.tif"),
            os.path.join(scene_dir, "*MSS*.tiff"),
            os.path.join(scene_dir, "*mss*.tif"),
            os.path.join(scene_dir, "*mss*.tiff"),
        ]
    )
    if image_path is None:
        raise FileNotFoundError("No MSS .tif/.tiff image found in {}".format(scene_dir))

    stem = os.path.splitext(os.path.basename(image_path))[0]
    metadata_path = _first_match(
        [
            os.path.join(scene_dir, stem + ".xml"),
            os.path.join(scene_dir, "*MSS*.xml"),
            os.path.join(scene_dir, "*mss*.xml"),
        ]
    )
    rpb_path = _first_match(
        [
            os.path.join(scene_dir, stem + ".rpb"),
            os.path.join(scene_dir, "*MSS*.rpb"),
            os.path.join(scene_dir, "*mss*.rpb"),
        ]
    )

    if metadata_path is None:
        raise FileNotFoundError("No MSS metadata XML found in {}".format(scene_dir))
    if rpb_path is None:
        raise FileNotFoundError("No MSS RPB file found in {}".format(scene_dir))

    return image_path, metadata_path, rpb_path


def prepare_output_dir(output_root, scene_dir):
    scene_name = os.path.basename(os.path.normpath(scene_dir))
    scene_output_dir = os.path.join(output_root, scene_name)
    os.makedirs(scene_output_dir, exist_ok=True)
    return scene_output_dir, scene_name


def radiometric_calibration(band_id, satellite_id, sensor_id, year, image_type, config):
    sensor_config = config["Parameter"][satellite_id][sensor_id]
    if sensor_id[:3] == "WFV":
        band_config = sensor_config[year]
    else:
        band_config = sensor_config[year][image_type]

    gain = band_config["gain"][band_id - 1]
    bias = band_config["offset"][band_id - 1]
    return gain, bias


def atmospheric_correction(band_id, metadata_path, config, satellite_id, sensor_id):
    dom = xml.dom.minidom.parse(metadata_path)

    s = SixS()
    s.geometry = Geometry.User()
    s.geometry.solar_z = 90 - float(dom.getElementsByTagName("SolarZenith")[0].firstChild.data)
    s.geometry.solar_a = float(dom.getElementsByTagName("SolarAzimuth")[0].firstChild.data)
    s.geometry.view_z = 0
    s.geometry.view_a = 0

    date = dom.getElementsByTagName("CenterTime")[0].firstChild.data.split(" ")[0].split("-")
    s.geometry.month = int(date[1])
    s.geometry.day = int(date[2])

    top_left_lat = float(dom.getElementsByTagName("TopLeftLatitude")[0].firstChild.data)
    top_left_lon = float(dom.getElementsByTagName("TopLeftLongitude")[0].firstChild.data)
    top_right_lat = float(dom.getElementsByTagName("TopRightLatitude")[0].firstChild.data)
    top_right_lon = float(dom.getElementsByTagName("TopRightLongitude")[0].firstChild.data)
    bottom_right_lat = float(dom.getElementsByTagName("BottomRightLatitude")[0].firstChild.data)
    bottom_right_lon = float(dom.getElementsByTagName("BottomRightLongitude")[0].firstChild.data)
    bottom_left_lat = float(dom.getElementsByTagName("BottomLeftLatitude")[0].firstChild.data)
    bottom_left_lon = float(dom.getElementsByTagName("BottomLeftLongitude")[0].firstChild.data)

    image_center_lat = (top_left_lat + top_right_lat + bottom_right_lat + bottom_left_lat) / 4
    if -15 < image_center_lat <= 15:
        s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.Tropical)
    elif 15 < image_center_lat <= 45:
        if 4 < s.geometry.month <= 9:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
        else:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeWinter)
    elif 45 < image_center_lat <= 60:
        if 4 < s.geometry.month <= 9:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.SubarcticSummer)
        else:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.SubarcticWinter)

    s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Continental)
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(0.36)
    s.aot550 = 0.14497

    point_ul = {
        "lat": max(top_left_lat, top_right_lat, bottom_right_lat, bottom_left_lat),
        "lon": min(top_left_lon, top_right_lon, bottom_right_lon, bottom_left_lon),
    }
    point_dr = {
        "lat": min(top_left_lat, top_right_lat, bottom_right_lat, bottom_left_lat),
        "lon": max(top_left_lon, top_right_lon, bottom_right_lon, bottom_left_lon),
    }
    mean_dem = MeanDEM(point_ul, point_dr) * 0.001

    s.altitudes = Altitudes()
    s.altitudes.set_target_custom_altitude(mean_dem)
    s.altitudes.set_sensor_satellite_level()

    srf_band = config["Parameter"][satellite_id][sensor_id]["SRF"][str(band_id)]
    if band_id == 1:
        s.wavelength = Wavelength(0.450, 0.520, srf_band)
    elif band_id == 2:
        s.wavelength = Wavelength(0.520, 0.590, srf_band)
    elif band_id == 3:
        s.wavelength = Wavelength(0.630, 0.690, srf_band)
    elif band_id == 4:
        s.wavelength = Wavelength(0.770, 0.890, srf_band)
    else:
        raise ValueError("Unsupported GF MSS band id: {}".format(band_id))

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(-0.1)
    s.run()
    return s.outputs.coef_xa, s.outputs.coef_xb, s.outputs.coef_xc


def block_process(dataset, output_dir, output_name, image_type, config, metadata_path, scene_info):
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize

    driver = gdal.GetDriverByName("GTiff")
    output_path = os.path.join(output_dir, output_name + ".tiff")
    out_dataset = driver.Create(output_path, cols, rows, 4, gdal.GDT_Int32)
    if out_dataset is None:
        raise RuntimeError("Failed to create output GeoTIFF: {}".format(output_path))

    out_dataset.SetGeoTransform(dataset.GetGeoTransform())
    out_dataset.SetProjection(dataset.GetProjection())

    block_size = 2048
    x_block_count = math.ceil(cols / block_size)
    y_block_count = math.ceil(rows / block_size)

    for band_id in range(1, 5):
        read_band = dataset.GetRasterBand(band_id)
        out_band = out_dataset.GetRasterBand(band_id)
        out_band.SetNoDataValue(-9999)

        gain, bias = radiometric_calibration(
            band_id,
            scene_info["satellite_id"],
            scene_info["sensor_id"],
            scene_info["calibration_year"],
            image_type,
            config,
        )
        coef_a, coef_b, coef_c = atmospheric_correction(
            band_id,
            metadata_path,
            config,
            scene_info["satellite_id"],
            scene_info["sensor_id"],
        )

        print("Processing band {}".format(band_id))
        with tqdm(total=x_block_count * y_block_count, desc="band {}".format(band_id), mininterval=10) as pbar:
            y_offset = 0
            while y_offset < rows:
                y_size = min(block_size, rows - y_offset)
                x_offset = 0
                while x_offset < cols:
                    x_size = min(block_size, cols - x_offset)
                    image = read_band.ReadAsArray(x_offset, y_offset, x_size, y_size)

                    radiance = np.where(image > 0, image * gain + bias, -9999)
                    y_value = np.where(radiance != -9999, coef_a * radiance - coef_b, -9999)
                    corrected = np.where(
                        y_value != -9999,
                        (y_value / (1 + y_value * coef_c)) * 10000,
                        -9999,
                    )

                    out_band.WriteArray(corrected, x_offset, y_offset)
                    x_offset += x_size
                    pbar.update(1)
                y_offset += y_size

        out_band.FlushCache()

    out_dataset.FlushCache()
    out_dataset = None
    return output_path


def process_scene(scene_dir, output_root, config, fallback_year):
    image_path, metadata_path, rpb_path = locate_mss_scene_files(scene_dir)
    output_dir, scene_name = prepare_output_dir(output_root, scene_dir)

    scene_info = load_scene_metadata(metadata_path)
    scene_info["calibration_year"] = resolve_calibration_year(
        config,
        scene_info["satellite_id"],
        scene_info["sensor_id"],
        scene_info["year"],
        fallback_year,
    )

    for source_path in (metadata_path, rpb_path):
        shutil.copy2(source_path, os.path.join(output_dir, os.path.basename(source_path)))

    dataset = gdal.Open(image_path)
    if dataset is None:
        raise RuntimeError("Failed to open image: {}".format(image_path))
    if dataset.RasterCount < 4:
        raise RuntimeError("Expected at least 4 MSS bands in image: {}".format(image_path))

    print("Scene: {}".format(scene_dir))
    print("Image: {}".format(image_path))
    print(
        "Sensor: {}/{}; image year: {}; calibration year: {}".format(
            scene_info["satellite_id"],
            scene_info["sensor_id"],
            scene_info["year"],
            scene_info["calibration_year"],
        )
    )

    return block_process(dataset, output_dir, scene_name, "MSS", config, metadata_path, scene_info)


def main(argv=None):
    start = time.time()
    args = parse_arguments(sys.argv[1:] if argv is None else argv)

    script_path = os.path.split(os.path.realpath(__file__))[0]
    config_file = os.path.join(script_path, "RadiometricCorrectionParameter.json")
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    os.makedirs(args.Output_dir, exist_ok=True)
    scenes = find_gf_scenes(args.Input_dir)
    if not scenes:
        raise FileNotFoundError("No GF MSS scene directories found in {}".format(args.Input_dir))

    outputs = []
    for scene_dir in scenes:
        outputs.append(process_scene(scene_dir, args.Output_dir, config, args.Fallback_year))

    print("Finished {} scene(s) in {:.1f}s".format(len(outputs), time.time() - start))
    for output_path in outputs:
        print("Output: {}".format(output_path))


if __name__ == "__main__":
    main()

