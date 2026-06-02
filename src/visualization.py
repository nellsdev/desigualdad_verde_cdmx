"""
Visualization helpers built on top of geemap.

Centralizes the map layout, palettes, and legend styling for the
NO2 + LST dual-layer view, so the same look-and-feel is reused across
notebooks in Sprints 1-3.
"""
from __future__ import annotations

import ee

from .config import (
    CDMX_CENTER,
    CDMX_ZOOM,
    LST_VIS_PARAMS,
    NDVI_VIS_PARAMS,
    NO2_VIS_PARAMS,
)


def build_dual_map(
    lst_image: ee.Image,
    no2_image: ee.Image,
    aoi: ee.FeatureCollection,
    center: list[float] | None = None,
    zoom: int | None = None,) -> "geemap.Map":
    
    """
    Build a toggleable dual-layer interactive map.

    Layers, in stacking order (top-most first):
        1. CDMX AOI outline (white, no fill, 2 px stroke).
        2. NO2 tropospheric column, 2023.
        3. Land Surface Temperature, summer 2023 (added last -> on top).

    Each raster layer is paired with a colorbar legend using the palettes
    from `src.config`.

    Args:
        lst_image: `ee.Image` with band `'LST_C'` (degrees Celsius).
        no2_image: `ee.Image` with band `'NO2_mol_m2'` (mol/m^2).
        aoi: `ee.FeatureCollection` for the AOI outline.
        center: Optional `[lat, lon]` override for the map center.
        zoom:   Optional zoom-level override (1-20).

    Returns:
        A `geemap.Map` instance ready to display in Jupyter / Colab.
    """
    import geemap  # local import keeps module importable without geemap installed

    m = geemap.Map(center=center or CDMX_CENTER, zoom=zoom or CDMX_ZOOM)

    # AOI outline (paint a 0-value image in white, 2px stroke).
    aoi_outline = ee.Image().paint(aoi, 0, 2)
    m.add_layer(aoi_outline, {"palette": ["white"]}, "CDMX AOI")

    # Raster layers.
    m.add_layer(
        lst_image,
        LST_VIS_PARAMS,
        "LST (°C) — Summer 2023",
    )
    m.add_layer(
        no2_image,
        NO2_VIS_PARAMS,
        "NO₂ (mol/m²) — 2023",
    )

    # Colorbar legends, one per layer.
    m.add_colorbar(
        LST_VIS_PARAMS,
        label="LST (°C)",
        layer_name="LST (°C) — Summer 2023",
    )
    m.add_colorbar(
        NO2_VIS_PARAMS,
        label="NO₂ (mol/m²)",
        layer_name="NO₂ (mol/m²) — 2023",
    )

    m.add_layer_control()
    return m


def build_triple_map(
    lst_image: ee.Image,
    no2_image: ee.Image,
    ndvi_image: ee.Image,
    aoi: ee.FeatureCollection,
    center: list[float] | None = None,
    zoom: int | None = None,
) -> "geemap.Map":
    """
    Build a toggleable triple-layer interactive map (LST + NO2 + NDVI).

    Layers, in stacking order from bottom to top of the map:
        1. NDVI  (added first)
        2. NO2
        3. LST
        4. CDMX AOI outline (added last, on top)

    In the layer control panel, the order is reversed (top to bottom):
        CDMX AOI, LST, NO2, NDVI — so the most important layers are
        at the top of the panel.

    Each raster layer is paired with a colorbar legend using the palettes
    from `src.config`.

    Args:
        lst_image:  `ee.Image` with band `'LST_C'`   (degrees Celsius).
        no2_image:  `ee.Image` with band `'NO2_mol_m2'` (mol/m^2).
        ndvi_image: `ee.Image` with band `'NDVI'`     (unitless).
        aoi:        `ee.FeatureCollection` for the AOI outline.
        center:     Optional `[lat, lon]` override for the map center.
        zoom:       Optional zoom-level override (1-20).

    Returns:
        A `geemap.Map` instance ready to display in Jupyter / Colab.
    """
    import geemap  # local import keeps module importable without geemap installed

    m = geemap.Map(center=center or CDMX_CENTER, zoom=zoom or CDMX_ZOOM)

    # Raster layers (NDVI added first so it sits at the bottom of the stack).
    m.add_layer(
        ndvi_image,
        NDVI_VIS_PARAMS,
        "NDVI — Summer 2023",
    )
    m.add_layer(
        no2_image,
        NO2_VIS_PARAMS,
        "NO₂ (mol/m²) — 2023",
    )
    m.add_layer(
        lst_image,
        LST_VIS_PARAMS,
        "LST (°C) — Summer 2023",
    )

    # AOI outline on top of all raster layers.
    aoi_outline = ee.Image().paint(aoi, 0, 2)
    m.add_layer(aoi_outline, {"palette": ["white"]}, "CDMX AOI")

    # Colorbar legends, one per layer.
    m.add_colorbar(
        NDVI_VIS_PARAMS,
        label="NDVI",
        layer_name="NDVI — Summer 2023",
    )
    m.add_colorbar(
        NO2_VIS_PARAMS,
        label="NO₂ (mol/m²)",
        layer_name="NO₂ (mol/m²) — 2023",
    )
    m.add_colorbar(
        LST_VIS_PARAMS,
        label="LST (°C)",
        layer_name="LST (°C) — Summer 2023",
    )

    m.add_layer_control()
    return m

