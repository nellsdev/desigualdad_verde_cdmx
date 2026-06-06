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
import pandas as pd

from .config import (
    SHAPEFILE_CDMX_ENT,
    SHAPEFILE_CDMX_MUN,
    SHAPEFILE_EDOMEX_MUN,
    NORTE_ZMVM,
    PERIFERIA_ZMVM,
    SUR_ZMVM,
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

def get_periferia_zmvm_aoi() -> ee.FeatureCollection:
    """
    Return the periphery of the ZMVM as a FeatureCollection combining:

    - All 16 CDMX alcaldías.
    - The 4 EdoMex municipios in ``PERIFERIA_ZMVM`` (Nezahualcóyotl,
      Ecatepec de Morelos, Naucalpan de Juárez, Tlalnepantla de Baz).

    Total: 20 features, all at the municipio level.

    Each feature carries the standard INEGI properties plus a convenient
    ``entidad`` label (``'CDMX'`` or ``'EdoMex'``) for downstream filtering
    or styling.

    Returns:
        ``ee.FeatureCollection`` with 20 features, reprojected to WGS84
        (EPSG:4326) so it can be passed directly to ``clip()`` or
        ``reduceRegions()``.

    Raises:
        FileNotFoundError: if either shapefile is missing.
        ValueError: if the EdoMex filter does not produce exactly 4 features
            (signals a spelling mismatch with the source ``NOMGEO`` field,
            typically after an INEGI rename).
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

    cdmx = gpd.read_file(SHAPEFILE_CDMX_MUN)
    edomex = gpd.read_file(SHAPEFILE_EDOMEX_MUN)

    periferia_edomex = edomex[edomex["NOMGEO"].isin(PERIFERIA_ZMVM)].copy()

    if len(periferia_edomex) != len(PERIFERIA_ZMVM):
        found = set(periferia_edomex["NOMGEO"])
        expected = set(PERIFERIA_ZMVM)
        missing = expected - found
        raise ValueError(
            f"Expected {len(PERIFERIA_ZMVM)} "
            f"periferia ZMVM municipios, found {len(periferia_edomex)}. "
            f"Missing from shapefile: {sorted(missing)}"
        )

    cdmx = cdmx.assign(entidad="CDMX")
    periferia_edomex = periferia_edomex.assign(entidad="EdoMex")

    combined = pd.concat([cdmx, periferia_edomex], ignore_index=True)
    if combined.crs is None:
        combined = combined.set_crs(epsg=4326)
    combined = combined.to_crs(epsg=4326)
    return geemap.gdf_to_ee(combined)


def _filter_cdmx_edomex_by_names(
    names: tuple[str, ...],
    label: str,
) -> "gpd.GeoDataFrame":
    """
    Internal helper: filter the CDMX municipio shapefile and the EdoMex
    municipio shapefile to the subset of names in ``names``, tag each
    row with its ``entidad`` label, and return a single concatenated
    GeoDataFrame in EPSG:4326.

    Used by ``get_norte_zmvm_aoi`` and ``get_sur_zmvm_aoi`` to avoid
    duplicating the filter / validate / concat logic.

    Args:
        names: Tuple of INEGI ``NOMGEO`` values (mix of CDMX alcaldías
            and EdoMex municipios allowed).
        label: Short human-readable label (e.g. ``"norte"``, ``"sur"``)
            used in the error message when a name is not found.

    Returns:
        ``GeoDataFrame`` in EPSG:4326, with columns including
        ``NOMGEO`` and ``entidad`` (``'CDMX'`` or ``'EdoMex'``).

    Raises:
        FileNotFoundError: if either shapefile is missing.
        ValueError: if any of the requested names is not present in the
            corresponding shapefile (signals a spelling mismatch with
            the source ``NOMGEO`` field).
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

    cdmx = gpd.read_file(SHAPEFILE_CDMX_MUN)
    edomex = gpd.read_file(SHAPEFILE_EDOMEX_MUN)

    cdmx_names = set(cdmx["NOMGEO"])
    edomex_names = set(edomex["NOMGEO"])

    matched_cdmx = [n for n in names if n in cdmx_names]
    matched_edomex = [n for n in names if n in edomex_names]
    missing = [n for n in names if n not in cdmx_names and n not in edomex_names]

    if missing:
        raise ValueError(
            f"Unknown {label} ZMVM names (not found in either CDMX or "
            f"EdoMex shapefiles): {sorted(missing)}"
        )

    cdmx_sub = cdmx[cdmx["NOMGEO"].isin(matched_cdmx)].copy().assign(entidad="CDMX")
    edomex_sub = (
        edomex[edomex["NOMGEO"].isin(matched_edomex)].copy().assign(entidad="EdoMex")
    )

    combined = pd.concat([cdmx_sub, edomex_sub], ignore_index=True)
    if combined.crs is None:
        combined = combined.set_crs(epsg=4326)
    combined = combined.to_crs(epsg=4326)
    return combined


def get_norte_zmvm_aoi() -> ee.FeatureCollection:
    """
    Return the northern periphery of the ZMVM as a FeatureCollection.

    Spans the "concrete belt" identified in Notebook 02:

    - 2 CDMX alcaldías: Gustavo A. Madero, Iztapalapa.
    - 4 EdoMex municipios: Tlalnepantla de Baz, Naucalpan de Juárez,
      Ecatepec de Morelos, Nezahualcóyotl.

    Total: 6 features, all at the municipio level.

    Returns:
        ``ee.FeatureCollection`` with 6 features in EPSG:4326.

    Raises:
        FileNotFoundError: if either shapefile is missing.
        ValueError: if any of the expected names is not found.
    """
    gdf = _filter_cdmx_edomex_by_names(NORTE_ZMVM, label="norte")
    return geemap.gdf_to_ee(gdf)


def get_sur_zmvm_aoi() -> ee.FeatureCollection:
    """
    Return the southern periphery of the ZMVM as a FeatureCollection.

    Spans the "green privilege" identified in Notebook 02:

    - 6 CDMX alcaldías: Coyoacán, Álvaro Obregón, Tlalpan, La Magdalena
      Contreras, Cuajimalpa de Morelos, Xochimilco.

    Total: 6 features, all at the municipio level.

    Returns:
        ``ee.FeatureCollection`` with 6 features in EPSG:4326.

    Raises:
        FileNotFoundError: if the CDMX shapefile is missing.
        ValueError: if any of the expected names is not found.
    """
    gdf = _filter_cdmx_edomex_by_names(SUR_ZMVM, label="sur")
    return geemap.gdf_to_ee(gdf)