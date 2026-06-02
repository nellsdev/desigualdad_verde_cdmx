"""
Project-wide configuration: paths, Earth Engine identifiers, band names,
and visualization parameter dictionaries.

All "magic strings" and "magic numbers" used by the GEE pipeline live here,
so a single edit propagates through every notebook.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Filesystem
# --------------------------------------------------------------------------- #
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

# Default AOI: INEGI Marco Geoestadistico, CDMX state boundary (entidad 09).
# One polygon, ~1,485 km^2. Replaced in Sprint 2 by the AGEB layer.
SHAPEFILE_CDMX_ENT: Path = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "shapefiles"
    / "09_ciudaddemexico"
    / "conjunto_de_datos"
    / "09ent.shp"
)

# Municipal-level boundaries (for the ZMVM choropleth and zonal stats).
SHAPEFILE_CDMX_MUN: Path = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "shapefiles"
    / "09_ciudaddemexico"
    / "conjunto_de_datos"
    / "09mun.shp"
)
SHAPEFILE_EDOMEX_MUN: Path = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "shapefiles"
    / "15_mexico"
    / "conjunto_de_datos"
    / "15mun.shp"
)

# CONAPO 2020 — the 60 Estado de México municipios that form the
# Zona Metropolitana del Valle de México (ZMVM) together with the 16
# CDMX alcaldías. Sourced from CONAPO "Delimitación de las zonas
# metropolitanas de México".
ZONE_METROPOLITANA_VALLE_MEXICO_EDOMEX_MUNS: tuple[str, ...] = (
    "Acolman", "Amecameca", "Apaxco", "Atenco", "Atizapán de Zaragoza",
    "Atlautla", "Axapusco", "Ayapango", "Coacalco de Berriozábal",
    "Cocotitlán", "Coyotepec", "Cuautitlán", "Cuautitlán Izcalli", "Chalco",
    "Chiautla", "Chicoloapan", "Chiconcuac", "Chimalhuacán",
    "Ecatepec de Morelos", "Ecatzingo", "Huehuetoca", "Hueypoxtla",
    "Huixquilucan", "Isidro Fabela", "Ixtapaluca", "Jaltenco", "Jilotzingo",
    "Juchitepec", "La Paz", "Lerma", "Melchor Ocampo", "Naucalpan de Juárez",
    "Nextlalpan", "Nezahualcóyotl", "Nicolás Romero", "Nopaltepec", "Ocoyoacac",
    "Otumba", "Ozumba", "Papalotla", "San Martín de las Pirámides", "Tecámac",
    "Temamatla", "Temascalapa", "Tenango del Aire", "Tenango del Valle",
    "Teoloyucan", "Tepetlaoxtoc", "Tepetlixpa", "Tepotzotlán", "Tequixquiac",
    "Texcoco", "Tezoyuca", "Tlalmanalco", "Tlalnepantla de Baz", "Tultepec",
    "Tultitlán", "Valle de Chalco Solidaridad", "Villa del Carbón", "Zumpango",
)


# --------------------------------------------------------------------------- #
# Earth Engine
# --------------------------------------------------------------------------- #
# Replace with the GCP project that has the Earth Engine API enabled.
# (Do NOT commit a real project ID to git.)
EE_PROJECT_ID: str = "ee-nrodriguezo2301"

# Collection identifiers.
LANDSAT8_ID: str = "LANDSAT/LC08/C02/T1_L2"
LANDSAT9_ID: str = "LANDSAT/LC09/C02/T1_L2"
SSP_NO2_ID: str = "COPERNICUS/SSP/OFFL/L3_NO2"
SSP_AER_ID: str = "COPERNICUS/SSP/OFFL/L3_AER_AI"

# Band names.
LANDSAT_BAND_THERMAL: str = "ST_B10"
LANDSAT_BAND_QA: str = "QA_PIXEL"
LANDSAT_BAND_NIR: str = "SR_B5"   # Near-Infrared (0.85-0.88 um)  — for NDVI
LANDSAT_BAND_RED: str = "SR_B4"   # Red           (0.64-0.67 um)  — for NDVI
S5P_BAND_NO2: str = "tropospheric_NO2_column_number_density"
# L3 NO2 has no qa_value; cloud_fraction is the standard quality proxy.
S5P_BAND_CLOUDFRAC: str = "cloud_fraction"

# --------------------------------------------------------------------------- #
# Visualization
# --------------------------------------------------------------------------- #
# CDMX centroid (Zocalo) and a comfortable zoom level for an AOI of this size.
CDMX_CENTER: list[float] = [19.4326, -99.1332]
CDMX_ZOOM: int = 11

# Land Surface Temperature (Celsius) — calibrated for CDMX summer 2023.
# Palette: cool -> warm -> hot (ColorBrewer "RdYlBu" reversed).
LST_VIS_PARAMS: dict = {
    "min": 22.0,
    "max": 45.0,
    "palette": [
        "#313695",  # 22  dark blue
        "#74add1",  # 27  light blue
        "#fed976",  # 32  pale yellow
        "#fd8d3c",  # 36  orange
        "#f31a1c",  # 41  red
        "#800026",  # 45  dark red
    ],
}

# Tropospheric NO2 column (mol/m^2) — calibrated for CDMX 2023 annual median.
# Palette: green (clean) -> yellow -> red -> purple (polluted).
NO2_VIS_PARAMS: dict = {
    "min": 5.0e-5,
    "max": 3.0e-4,
    "palette": [
        "#1a9850",  # clean
        "#a6d96a",
        "#fee08b",
        "#f46d43",
        "#a50026",
        "#762a83",  # polluted
    ],
}

# NDVI — calibrated for CDMX summer 2023.
# Range -0.1 .. 0.7 captures bare soil (-0.1) to dense vegetation (0.7).
# Palette: red (no vegetation) -> yellow -> dark green (dense vegetation).
NDVI_VIS_PARAMS: dict = {
    "min": -0.1,
    "max": 0.7,
    "palette": [
        "#d7191c",  # bare soil / impervious surface
        "#fdae61",
        "#ffffbf",  # sparse vegetation
        "#a6d96a",
        "#1a9850",  # dense vegetation
    ],
}
