from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

from atmcorr.common.dem import GeoBounds
from atmcorr.common.sixs import SixSGeometry


@dataclass(frozen=True)
class GFSceneMetadata:
    satellite_id: str
    sensor_id: str
    center_time: datetime
    solar_z: float
    solar_a: float
    bounds: GeoBounds
    center_lat: float
    center_lon: float

    @property
    def year(self) -> str:
        return str(self.center_time.year)

    def sixs_geometry(self) -> SixSGeometry:
        return SixSGeometry(
            solar_z=self.solar_z,
            solar_a=self.solar_a,
            view_z=0.0,
            view_a=0.0,
            month=self.center_time.month,
            day=self.center_time.day,
            center_lat=self.center_lat,
        )


def _text(root: ET.Element, tag: str, metadata_path: Path) -> str:
    node = root.find(f".//{tag}")
    if node is None or node.text is None:
        raise ValueError(f"Missing metadata tag '{tag}' in {metadata_path}")
    return node.text.strip()


def load_gf_metadata(metadata_path: str | Path) -> GFSceneMetadata:
    path = Path(metadata_path)
    root = ET.parse(path).getroot()

    center_time_text = _text(root, "CenterTime", path)
    center_time = datetime.strptime(center_time_text.split(".")[0], "%Y-%m-%d %H:%M:%S")

    lats = [
        float(_text(root, "TopLeftLatitude", path)),
        float(_text(root, "TopRightLatitude", path)),
        float(_text(root, "BottomRightLatitude", path)),
        float(_text(root, "BottomLeftLatitude", path)),
    ]
    lons = [
        float(_text(root, "TopLeftLongitude", path)),
        float(_text(root, "TopRightLongitude", path)),
        float(_text(root, "BottomRightLongitude", path)),
        float(_text(root, "BottomLeftLongitude", path)),
    ]

    # Keep the legacy interpretation: metadata SolarZenith is used as elevation.
    solar_z = 90.0 - float(_text(root, "SolarZenith", path))

    return GFSceneMetadata(
        satellite_id=_text(root, "SatelliteID", path),
        sensor_id=_text(root, "SensorID", path),
        center_time=center_time,
        solar_z=solar_z,
        solar_a=float(_text(root, "SolarAzimuth", path)),
        bounds=GeoBounds(
            min_lat=min(lats),
            max_lat=max(lats),
            min_lon=min(lons),
            max_lon=max(lons),
        ),
        center_lat=sum(lats) / len(lats),
        center_lon=sum(lons) / len(lons),
    )
