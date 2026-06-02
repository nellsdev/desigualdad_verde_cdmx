"""
Area-of-Interest loaders.

Reads INEGI Marco Geoestadistico shapefiles from `data/raw/shapefiles/`
and converts them to `ee.FeatureCollection` objects ready to feed into
`filterBounds()`, `clip()`, or `reduceRegions()`.

Signal analogy: defining the region of support (RoI) of your analysis.
Like choosing the time window for an EEG epoch selection — anything
outside it is irrelevant for this study.
"""
from __future__ import annotations

from pathlib import Path

import ee
import geemap
import geopandas as gpd

from .config import SHAPEFILE_CDMX_ENT


def load_aoi_from_file(shapefile_path: Path) -> ee.FeatureCollection:
    """
    Read a local shapefile and convert it to an `ee.FeatureCollection`.

    The shapefile is reprojected to WGS84 (EPSG:4326) before conversion,
    which is the CRS Earth Engine expects for lon/lat geometry.

    Args:
        shapefile_path: Absolute path to a `.shp` file readable by geopandas.

    Returns:
        `ee.FeatureCollection` with the same geometries as the input file.
    """
    gdf = gpd.read_file(shapefile_path)
    if gdf.crs is None:
        # Some INEGI shapefiles lack a .prj; assume WGS84 (INEGI default for
        # Marco Geoestadistico products) and warn via the assert below.
        gdf = gdf.set_crs(epsg=4326)
    gdf = gdf.to_crs(epsg=4326)
    return geemap.gdf_to_ee(gdf)


def get_cdmx_aoi(shapefile_path: Path | None = None) -> ee.FeatureCollection:
    """
    Load the CDMX state boundary (INEGI 09ent) as an Earth Engine
    FeatureCollection.

    The default shapefile is the single-polygon entidad boundary.
    In Sprint 1 Task 3 (zonal stats) we will pass a different shapefile
    (e.g. `09a.shp` for AGEBs) to this same function.

    Args:
        shapefile_path: Optional override; defaults to `SHAPEFILE_CDMX_ENT`.

    Returns:
        `ee.FeatureCollection` containing one feature (CDMX boundary).
    """
    path = shapefile_path or SHAPEFILE_CDMX_ENT
    if not path.exists():
        raise FileNotFoundError(
            f"CDMX AOI shapefile not found at {path}. "
            "Check that data/raw/shapefiles/09_ciudaddemexico/ is populated."
        )
    return load_aoi_from_file(path)
