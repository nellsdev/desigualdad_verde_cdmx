"""
Sentinel-5P TROPOMI NO2 helpers.

We use the OFFL/L3 gridded product, which provides the tropospheric
NO2 column number density in mol/m^2.

Quality control: the L3 product does not include a `qa_value` band
(as the L2 product does). The standard cloud-contamination proxy on
L3 is the `cloud_fraction` band — we keep pixels with cloud_fraction
below a configurable threshold.

Reference: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_NO2
"""
from __future__ import annotations

import warnings
from typing import Optional

import ee

from .config import S5P_BAND_CLOUDFRAC, S5P_BAND_NO2, SSP_NO2_ID


def mask_no2_clouds(image: ee.Image, cloud_max: float = 0.3) -> ee.Image:
    """
    Mask out pixels contaminated by clouds (cloud_fraction >= cloud_max).

    The L3 NO2 product exposes scene-level cloud cover per pixel via the
    `cloud_fraction` band (range 0-1). Pixels with high cloud_fraction
    have unreliable tropospheric NO2 retrievals and are dropped.

    Signal analogy: cloud rejection — like dropping EEG epochs with
    impedance spikes; the underlying neural signal is still there but
    is not measurable cleanly.

    Args:
        image: A Sentinel-5P L3 NO2 `ee.Image` containing `cloud_fraction`.
        cloud_max: Maximum acceptable cloud fraction in [0, 1]
            (default 0.3, i.e. drop pixels >= 30% cloud cover).

    Returns:
        The same image with cloudy pixels masked.
    """
    return image.updateMask(image.select(S5P_BAND_CLOUDFRAC).lt(cloud_max))


def load_no2_composite(
    aoi: ee.FeatureCollection,
    start_date: str,
    end_date: str,
    cloud_max: Optional[float] = None,
    qa_min: Optional[float] = None,
) -> ee.Image:
    """
    Annual (or arbitrary-period) median NO2 tropospheric column over the AOI,
    in mol/m^2.

    Annual median cancels out seasonal/meteorological variability and
    delivers a stable spatial pattern. Daily overpasses are noisy.

    Args:
        aoi: `ee.FeatureCollection` defining the region of interest.
        start_date: ISO date string, inclusive.
        end_date:   ISO date string, exclusive.
        cloud_max:  Maximum acceptable `cloud_fraction` in [0, 1]
            (default 0.3 if neither `cloud_max` nor `qa_min` is given).
        qa_min:     DEPRECATED. Old L2-style parameter (kept for
            backward compatibility with notebooks written before the
            S5P L3 schema was adopted). Internally converted to
            `cloud_max = 1 - qa_min`. If both `qa_min` and `cloud_max`
            are given, `cloud_max` wins and a warning is emitted.

    Returns:
        Single-band `ee.Image` (band name `'NO2_mol_m2'`, mol/m^2),
        clipped to the AOI.
    """
    if qa_min is not None:
        # Backward-compat: notebooks written before the L3 migration
        # used qa_value >= qa_min. Translate to the equivalent
        # cloud_fraction threshold so the old call still works.
        if cloud_max is None:
            cloud_max = 1.0 - qa_min
            warnings.warn(
                "`qa_min` is deprecated for the S5P L3 product "
                "(no `qa_value` band). Use `cloud_max` instead. "
                "Translated qa_min=%.2f -> cloud_max=%.2f."
                % (qa_min, cloud_max),
                UserWarning,
                stacklevel=2,
            )
        else:
            warnings.warn(
                "Both `qa_min` and `cloud_max` were passed; using `cloud_max` "
                "and ignoring `qa_min`.",
                UserWarning,
                stacklevel=2,
            )

    if cloud_max is None:
        cloud_max = 0.3

    collection = (
        ee.ImageCollection(SSP_NO2_ID)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .map(lambda img: mask_no2_clouds(img, cloud_max))
    )
    return (
        collection
        .select(S5P_BAND_NO2)
        .median()
        .clip(aoi)
        .rename("NO2_mol_m2")
    )

