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
PERIFERIA_ZMVM: tuple[str, ...] = (
    "Nezahualcóyotl", "Ecatepec de Morelos", "Naucalpan de Juárez", "Tlalnepantla de Baz",
)
# Northern ZMVM: the concrete belt — 2 CDMX alcaldías + 4 EdoMex municipios.
# Used for the zoomed-in "ground zero" view in Notebook 02 (Map 2).
NORTE_ZMVM: tuple[str, ...] = (
    "Gustavo A. Madero", "Iztapalapa",
    "Tlalnepantla de Baz", "Naucalpan de Juárez",
    "Ecatepec de Morelos", "Nezahualcóyotl",
)
# Southern ZMVM: the green privilege — 6 CDMX alcaldías (Cuajimalpa uses its
# full INEGI name "Cuajimalpa de Morelos" in the shapefile).
# Used for the zoomed-in southern view in Notebook 02 (Map 3).
SUR_ZMVM: tuple[str, ...] = (
    "Coyoacán", "Álvaro Obregón", "Tlalpan", "La Magdalena Contreras",
    "Cuajimalpa de Morelos", "Xochimilco",
)
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
S5P_NO2_ID: str = "COPERNICUS/S5P/OFFL/L3_NO2"
S5P_AER_ID: str = "COPERNICUS/S5P/OFFL/L3_AER_AI"

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
    "min": 2.0e-5,
    "max": 2.5e-4,
    "palette": [
        "#1a9850",  # clean
        "#a6d96a",
        "#fee08b",
        "#f46d43",
        "#a50026",
        "#762a83",  # polluted
    ],
}

# NDVI indice
# Range 0.1 .. 0.8 captures the full spectrum of vegetation health in CDMX.
# Range near to 0 or negative captures no vegetation at all (urban, water, bare
# soil). Range above 0.8 is rare and usually noise (e.g. clouds).
# ColorBrewer YlGn-style palette: pale yellow (arid, concrete surfaces) at the
# low end, dark blue (dense, healthy forest) at the high end.
NDVI_VIS_PARAMS: dict = {
    "min": 0.1,
    "max": 0.8,
    "palette": [
        "#ffffe5",  # concrete / no vegetation (pale yellow-white)
        "#c7e9b4",  # sparse vegetation (light green)
        "#7fcdbb",  # moderate vegetation (medium green-teal)
        "#41b6c4",  # healthy vegetation (teal)
        "#1d91c0",  # dense vegetation (blue)
        "#225ea8",  # very dense forest (dark blue)
    ],
}
