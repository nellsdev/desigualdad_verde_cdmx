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

from .config import (
    SHAPEFILE_CDMX_ENT,
    SHAPEFILE_CDMX_MUN,
    SHAPEFILE_EDOMEX_MUN,
    ZONE_METROPOLITANA_VALLE_MEXICO_EDOMEX_MUNS,
)


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


def get_zmvm_municipalities_aoi() -> ee.FeatureCollection:
    """
    Return the Zona Metropolitana del Valle de México as a FeatureCollection
    of 76 municipal polygons: the 16 CDMX alcaldías plus the 60 Estado de
    México municipios in the CONAPO 2020 delimitation.

    Each feature carries the standard INEGI properties (``CVEGEO``,
    ``CVE_ENT``, ``CVE_MUN``, ``NOMGEO``) plus a convenient ``entidad``
    label (``'CDMX'`` or ``'EdoMex'``) for downstream filtering or styling.

    Returns:
        ``ee.FeatureCollection`` with 76 features, reprojected to WGS84
        (EPSG:4326) so it can be passed directly to ``clip()`` or
        ``reduceRegions()``.

    Raises:
        FileNotFoundError: if either municipal shapefile is missing.
        ValueError: if the EdoMex filter does not produce exactly 60
            features (signals a spelling mismatch with the source
            ``NOMGEO`` field, typically after an INEGI rename).
    """
    if not SHAPEFILE_CDMX_MUN.exists():
        raise FileNotFoundError(
            f"CDMX municipios shapefile not found at {SHAPEFILE_CDMX_MUN}. "
            "Check that data/raw/shapefiles/09_ciudaddemexico/ is populated."
        )
    if not SHAPEFILE_EDOMEX_MUN.exists():
        raise FileNotFoundError(
            f"EdoMex municipios shapefile not found at {SHAPEFILE_EDOMEX_MUN}. "
            "Check that data/raw/shapefiles/15_mexico/ is populated."
        )

    import pandas as pd  # local import keeps this module lean

    cdmx = gpd.read_file(SHAPEFILE_CDMX_MUN)
    edomex = gpd.read_file(SHAPEFILE_EDOMEX_MUN)

    edomex_zmvm = edomex[
        edomex["NOMGEO"].isin(ZONE_METROPOLITANA_VALLE_MEXICO_EDOMEX_MUNS)
    ].copy()

    if len(edomex_zmvm) != len(ZONE_METROPOLITANA_VALLE_MEXICO_EDOMEX_MUNS):
        found = set(edomex_zmvm["NOMGEO"])
        expected = set(ZONE_METROPOLITANA_VALLE_MEXICO_EDOMEX_MUNS)
        missing = expected - found
        raise ValueError(
            f"Expected {len(ZONE_METROPOLITANA_VALLE_MEXICO_EDOMEX_MUNS)} "
            f"EdoMex ZMVM municipios, found {len(edomex_zmvm)}. "
            f"Missing from shapefile: {sorted(missing)}"
        )

    cdmx = cdmx.assign(entidad="CDMX")
    edomex_zmvm = edomex_zmvm.assign(entidad="EdoMex")

    combined = pd.concat([cdmx, edomex_zmvm], ignore_index=True)
    if combined.crs is None:
        combined = combined.set_crs(epsg=4326)
    combined = combined.to_crs(epsg=4326)
    return geemap.gdf_to_ee(combined)
