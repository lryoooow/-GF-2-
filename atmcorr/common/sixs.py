from __future__ import annotations

from dataclasses import dataclass

from Py6S import (
    AeroProfile,
    Altitudes,
    AtmosCorr,
    AtmosProfile,
    Geometry,
    GroundReflectance,
    SixS,
    Wavelength,
)


@dataclass(frozen=True)
class SixSOptions:
    aot550: float = 0.14497
    ground_reflectance: float = 0.36
    aerosol_profile: str = "Continental"


@dataclass(frozen=True)
class SixSGeometry:
    solar_z: float
    solar_a: float
    view_z: float
    view_a: float
    month: int
    day: int
    center_lat: float


def atmospheric_profile_for_latitude(center_lat: float, month: int):
    if -15 < center_lat <= 15:
        return AtmosProfile.Tropical
    if 15 < center_lat <= 45:
        if 4 < month <= 9:
            return AtmosProfile.MidlatitudeSummer
        return AtmosProfile.MidlatitudeWinter
    if 45 < center_lat <= 60:
        if 4 < month <= 9:
            return AtmosProfile.SubarcticSummer
        return AtmosProfile.SubarcticWinter
    return AtmosProfile.MidlatitudeSummer if 4 < month <= 9 else AtmosProfile.MidlatitudeWinter


def aerosol_profile_from_name(name: str):
    try:
        return getattr(AeroProfile, name)
    except AttributeError as exc:
        raise ValueError(f"Unsupported aerosol profile: {name}") from exc


def correction_coefficients(
    geometry: SixSGeometry,
    target_altitude_km: float,
    wavelength: Wavelength,
    options: SixSOptions,
) -> tuple[float, float, float]:
    sixs = SixS()
    sixs.geometry = Geometry.User()
    sixs.geometry.solar_z = geometry.solar_z
    sixs.geometry.solar_a = geometry.solar_a
    sixs.geometry.view_z = geometry.view_z
    sixs.geometry.view_a = geometry.view_a
    sixs.geometry.month = geometry.month
    sixs.geometry.day = geometry.day

    sixs.atmos_profile = AtmosProfile.PredefinedType(
        atmospheric_profile_for_latitude(geometry.center_lat, geometry.month)
    )
    sixs.aero_profile = AeroProfile.PredefinedType(
        aerosol_profile_from_name(options.aerosol_profile)
    )
    sixs.ground_reflectance = GroundReflectance.HomogeneousLambertian(
        options.ground_reflectance
    )
    sixs.aot550 = options.aot550

    sixs.altitudes = Altitudes()
    sixs.altitudes.set_target_custom_altitude(target_altitude_km)
    sixs.altitudes.set_sensor_satellite_level()

    sixs.wavelength = wavelength
    sixs.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(-0.1)
    sixs.run()
    return sixs.outputs.coef_xa, sixs.outputs.coef_xb, sixs.outputs.coef_xc
