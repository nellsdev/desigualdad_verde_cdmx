"""
Project 1: Dos Méxicos Bajo el Mismo Sol.

A modular Python package for analyzing urban heat islands, air quality,
and environmental justice in CDMX via Google Earth Engine.

Modules:
    config         Paths, project ID, vis parameter dicts, band-name constants.
    aoi            Load INEGI shapefiles (CDMX boundary, AGEBs) as ee.FeatureCollection.
    landsat        Cloud mask + LST calibration + median composite loader.
    sentinel5p     NO2 quality mask + median composite loader.
    visualization  geemap builders, color palettes, colorbar helpers.
"""

from __future__ import annotations

__version__ = "0.1.0"

# Re-export the public API so callers can do:
#     from src import get_cdmx_aoi, load_lst_composite, ...
from .aoi import (
    get_cdmx_aoi,
    get_norte_zmvm_aoi,
    get_periferia_zmvm_aoi,
    get_sur_zmvm_aoi,
    get_zmvm_municipalities_aoi,
    load_aoi_from_file,
)
from .config import (
    CDMX_CENTER,
    CDMX_ZOOM,
    EE_PROJECT_ID,
    LANDSAT_BAND_NIR,
    LANDSAT_BAND_QA,
    LANDSAT_BAND_RED,
    LANDSAT_BAND_THERMAL,
    LST_VIS_PARAMS,
    NDVI_VIS_PARAMS,
    NO2_VIS_PARAMS,
    PROJECT_ROOT,
    S5P_BAND_CLOUDFRAC,
    S5P_BAND_NO2,
    SHAPEFILE_CDMX_ENT,
    PERIFERIA_ZMVM,
)
from .landsat import calculate_lst, load_lst_composite, mask_clouds_shadows
from .landsat import (
    calculate_lst,
    calculate_ndvi,
    load_lst_composite,
    load_ndvi_composite,
    mask_clouds_shadows,
)
from .sentinel5p import load_no2_composite, mask_no2_clouds
from .visualization import build_dual_map, build_triple_map

__all__ = [
    "__version__",
    # aoi
    "get_cdmx_aoi",
    "get_norte_zmvm_aoi",
    "get_periferia_zmvm_aoi",
    "get_sur_zmvm_aoi",
    "get_zmvm_municipalities_aoi",
    "load_aoi_from_file",
    # config
    "PROJECT_ROOT",
    "SHAPEFILE_CDMX_ENT",
    "PERIFERIA_ZMVM",
    "ZONE_METROPOLITANA_VALLE_MEXICO_EDOMEX_MUNS",
    "EE_PROJECT_ID",
    "CDMX_CENTER",
    "CDMX_ZOOM",
    "LST_VIS_PARAMS",
    "NO2_VIS_PARAMS",
    "NDVI_VIS_PARAMS",
    "S5P_BAND_NO2",
    "S5P_BAND_CLOUDFRAC",
    "LANDSAT_BAND_THERMAL",
    "LANDSAT_BAND_QA",
    "LANDSAT_BAND_NIR",
    "LANDSAT_BAND_RED",
    # landsat
    "mask_clouds_shadows",
    "calculate_lst",
    "calculate_ndvi",
    "load_lst_composite",
    "load_ndvi_composite",
    # sentinel5p
    "mask_no2_clouds",
    "load_no2_composite",
    # visualization
    "build_map",
    "build_dual_map",
    "build_triple_map",
]
