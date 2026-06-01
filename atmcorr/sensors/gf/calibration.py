from __future__ import annotations

import json
from pathlib import Path

from Py6S import Wavelength

from atmcorr.common.constants import DEFAULT_CALIBRATION_PATH


GF_MSS_WAVELENGTHS = {
    1: (0.450, 0.520),
    2: (0.520, 0.590),
    3: (0.630, 0.690),
    4: (0.770, 0.890),
}


def load_calibration_config(path: str | Path = DEFAULT_CALIBRATION_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def resolve_calibration_year(
    config: dict,
    satellite_id: str,
    sensor_id: str,
    image_year: str,
    fallback_year: str,
) -> str:
    sensor_config = config["Parameter"][satellite_id][sensor_id]
    if image_year in sensor_config:
        return image_year
    if fallback_year in sensor_config:
        print(
            "WARNING: calibration parameters for {}/{}/{} are missing; using {} "
            "for smoke testing only.".format(
                satellite_id, sensor_id, image_year, fallback_year
            )
        )
        return fallback_year
    available = sorted(key for key in sensor_config if key.isdigit())
    raise KeyError(
        "No calibration parameters for {}/{}/{}. Available years: {}".format(
            satellite_id, sensor_id, image_year, ", ".join(available)
        )
    )


def gain_bias(
    config: dict,
    satellite_id: str,
    sensor_id: str,
    year: str,
    image_type: str,
    band_id: int,
) -> tuple[float, float]:
    sensor_config = config["Parameter"][satellite_id][sensor_id]
    band_config = sensor_config[year] if sensor_id[:3] == "WFV" else sensor_config[year][image_type]
    return band_config["gain"][band_id - 1], band_config["offset"][band_id - 1]


def wavelength(config: dict, satellite_id: str, sensor_id: str, band_id: int) -> Wavelength:
    start, end = GF_MSS_WAVELENGTHS[band_id]
    srf = config["Parameter"][satellite_id][sensor_id]["SRF"][str(band_id)]
    return Wavelength(start, end, srf)
