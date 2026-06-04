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

# Municipal-level boundaries used to build the ZMVM clipping polygon
# (16 CDMX alcaldías + 60 EdoMex municipios, CONAPO 2020 delimitation).
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

# CONAPO 2020 — the 60 Estado de México municipios that, together with the 16
# CDMX alcaldías, form the Zona Metropolitana del Valle de México (ZMVM).
# Source: CONAPO "Delimitación de las Zonas Metropolitanas de México", with
# the 2020 ZMVM revision. Spelling (including diacritics) must match the
# NOMGEO field of `15mun.shp` exactly.
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
LANDSAT_COLLECTION_ID: str = "LANDSAT/LC08/C02/T1_L2"
S5P_NO2_COLLECTION_ID: str = "COPERNICUS/S5P/OFFL/L3_NO2"

# Band names.
LANDSAT_BAND_THERMAL: str = "ST_B10"
LANDSAT_BAND_QA: str = "QA_PIXEL"
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
