"""
Landsat 8/9 Collection 2 Level 2 helpers.

Pipeline per image:
    raw ST_B10 (DN)  --multiply 0.00341802 + add 149.0-->  Kelvin
                     --subtract 273.15-->                  Celsius

Reference: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2
"""
from __future__ import annotations

import ee

from .config import (
    LANDSAT_BAND_NIR,
    LANDSAT_BAND_QA,
    LANDSAT_BAND_RED,
    LANDSAT_BAND_THERMAL,
    LANDSAT8_ID,
    LANDSAT9_ID,
)


def mask_clouds_shadows(image: ee.Image) -> ee.Image:
    """
    Mask clouds (bit 3) and cloud shadow (bit 4) using the QA_PIXEL bitmask.

    Args:
        image: A Landsat 8/9 C02 L2 `ee.Image`. Must contain `QA_PIXEL`.

    Returns:
        The same image with a cloud/shadow mask applied to all bands.
    """
    qa = image.select(LANDSAT_BAND_QA)
    cloud_bit = 1 << 3
    shadow_bit = 1 << 4
    mask = qa.bitwiseAnd(cloud_bit).eq(0).And(
        qa.bitwiseAnd(shadow_bit).eq(0)
    )
    return image.updateMask(mask)


def calculate_lst(image: ee.Image) -> ee.Image:
    """
    Convert ST_B10 (DN) to Land Surface Temperature in Celsius.

    Formula (Collection 2 scaling):  K = DN * 0.00341802 + 149.0
                                     C = K - 273.15

    Args:
        image: A Landsat 8/9 C02 L2 `ee.Image`. Must contain `ST_B10`.

    Returns:
        The same image with a new `'LST_C'` band added (in degrees Celsius).
    """
    lst_kelvin = (
        image.select(LANDSAT_BAND_THERMAL).multiply(0.00341802).add(149.0)
    )
    lst_celsius = lst_kelvin.subtract(273.15).rename("LST_C")
    return image.addBands(lst_celsius)


def load_lst_composite(
    aoi: ee.FeatureCollection,
    start_date: str,
    end_date: str,
    cloud_max: float = 20.0,
) -> ee.Image:
    """
    Cloud-masked median Land Surface Temperature composite over the AOI.

    Args:
        aoi: `ee.FeatureCollection` defining the region of interest.
        start_date: ISO date string, inclusive (e.g. `'2023-06-01'`).
        end_date:   ISO date string, exclusive   (e.g. `'2023-09-01'`).
        cloud_max:  Maximum scene-level cloud cover percentage (default 20).

    Returns:
        Single-band `ee.Image` (band name `'LST_C'`, degrees Celsius),
        clipped to the AOI.
    """
    
    # Load LANDSAT 8 and 9 sataellites and merge them into a single collection.
    l8 = ee.ImageCollection(LANDSAT8_ID)
    l9 = ee.ImageCollection(LANDSAT9_ID)
    landsat_collection = l8.merge(l9)

    # Filter Level 1: Complete Images by AOI, date, and cover clouds (20% threshold is common for LST studies).
    # Filter Level 2: Pixel Mask clouds and shadows, then calculate LST in Celsius.
    collection = (
        landsat_collection.filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte("CLOUD_COVER", cloud_max))
        .map(mask_clouds_shadows)
        .map(calculate_lst)
    )
    return collection.select("LST_C").median().clip(aoi)


def calculate_ndvi(image: ee.Image) -> ee.Image:
    """
    Compute the Normalized Difference Vegetation Index from a Landsat 8/9
    Collection 2 L2 image.

    NDVI = (NIR - Red) / (NIR + Red)
         = (SR_B5 - SR_B4) / (SR_B5 + SR_B4)

    Range: -1 (water / impervious) to +1 (dense vegetation). Typical
    CDMX summer values: 0.1 (urban) to 0.7 (forest).

    Signal analogy: NDVI is the coherence between the NIR and Red
    channels — like a normalized cross-correlation between two signals.
    `normalizedDifference` in GEE handles the divide-by-zero case
    safely (returns 0 where NIR + Red = 0).

    Args:
        image: A Landsat 8/9 C02 L2 `ee.Image`. Must contain `SR_B4`
            and `SR_B5`.

    Returns:
        The same image with a new `'NDVI'` band added (unitless, [-1, 1]).
    """
    ndvi = (
        image
        .normalizedDifference([LANDSAT_BAND_NIR, LANDSAT_BAND_RED])
        .rename("NDVI")
    )
    return image.addBands(ndvi)


def load_ndvi_composite(
    aoi: ee.FeatureCollection,
    start_date: str,
    end_date: str,
    cloud_max: float = 20.0,
) -> ee.Image:
    """
    Cloud-masked median NDVI composite over the AOI.

    Signal analogy: same ERP-style averaging as `load_lst_composite`,
    applied to the vegetation channel instead of the thermal channel.
    The same scene cloud-mask is reused, since clouds contaminate both
    the optical (NDVI) and thermal (LST) bands.

    Args:
        aoi: `ee.FeatureCollection` defining the region of interest.
        start_date: ISO date string, inclusive.
        end_date:   ISO date string, exclusive.
        cloud_max:  Maximum scene-level cloud cover percentage (default 20).

    Returns:
        Single-band `ee.Image` (band name `'NDVI'`, unitless),
        clipped to the AOI.
    """
    collection = (
        ee.ImageCollection()
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filterMetadata("CLOUD_COVER", "less_than", cloud_max)
        .map(mask_clouds_shadows)
        .map(calculate_ndvi)
    )
    return collection.select("NDVI").median().clip(aoi)
