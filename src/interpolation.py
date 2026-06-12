"""
Spatial interpolation of air quality data using Ordinary Kriging.

Builds a continuous surface from point measurements (SINAICA stations)
so pollution estimates are available everywhere, not just at monitor locations.

Requires ``pykrige`` (install with ``pip install pykrige``).
Falls back to a simple IDW warning if pykrige is not available.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def _idw_fallback(
    station_df: pd.DataFrame,
    grid_lng: np.ndarray,
    grid_lat: np.ndarray,
) -> np.ndarray:
    """Simple inverse-distance-weighted fallback when PyKrige is missing."""
    from scipy.spatial.distance import cdist

    coords = station_df[["lng", "lat"]].values
    values = station_df["value"].values
    grid = np.column_stack([grid_lng.ravel(), grid_lat.ravel()])

    dist = cdist(grid, coords)
    dist[dist < 1e-10] = 1e-10
    w = 1.0 / dist ** 2
    estimates = (w @ values) / w.sum(axis=1)
    return estimates.reshape(grid_lng.shape)


def kriging_surface(
    station_df: pd.DataFrame,
    resolution: float = 0.02,
    pad: float = 0.05,
    variogram_model: str = "spherical",
) -> dict:
    """Interpolate point measurements onto a regular grid using Ordinary Kriging.

    Parameters
    ----------
    station_df : pd.DataFrame
        Must have columns ``lng``, ``lat``, ``value``.
        One row per station with the annual mean value to interpolate.
    resolution : float
        Grid cell size in degrees (default 0.02 ≈ 2.2 km at CDMX latitude).
    pad : float
        Degrees of padding around the station bounding box (default 0.05).
    variogram_model : str
        Variogram model for PyKrige: ``"spherical"``, ``"exponential"``,
        ``"gaussian"``, ``"linear"`` (default ``"spherical"``).

    Returns
    -------
    dict with keys:
        - lng: 2D array of longitudes
        - lat: 2D array of latitudes
        - z:   2D array of interpolated values
        - sigma: 2D array of kriging standard deviation (None if IDW fallback)
        - method: ``"ordinary_kriging"`` or ``"idw_fallback"``
    """
    coords = station_df[["lng", "lat"]].values
    values = station_df["value"].values.astype(float)

    # Build grid
    lng_min, lng_max = coords[:, 0].min(), coords[:, 0].max()
    lat_min, lat_max = coords[:, 1].min(), coords[:, 1].max()
    grid_lng = np.arange(lng_min - pad, lng_max + pad, resolution)
    grid_lat = np.arange(lat_min - pad, lat_max + pad, resolution)
    grid_lng_2d, grid_lat_2d = np.meshgrid(grid_lng, grid_lat)

    try:
        from pykrige.ok import OrdinaryKriging

        OK = OrdinaryKriging(
            coords[:, 0],
            coords[:, 1],
            values,
            variogram_model=variogram_model,
            verbose=False,
            enable_plotting=False,
        )
        z, sigma = OK.execute("grid", grid_lng, grid_lat)
        return {
            "lng": grid_lng_2d,
            "lat": grid_lat_2d,
            "z": z,
            "sigma": sigma,
            "method": "ordinary_kriging",
        }
    except ImportError:
        import warnings

        warnings.warn(
            "pykrige is not installed. Falling back to IDW interpolation. "
            "Install with: pip install pykrige",
            UserWarning,
        )
        z = _idw_fallback(station_df, grid_lng_2d, grid_lat_2d)
        return {
            "lng": grid_lng_2d,
            "lat": grid_lat_2d,
            "z": z,
            "sigma": None,
            "method": "idw_fallback",
        }


def prepare_station_data(
    annual_stats: pd.DataFrame,
    pollutant: str,
    stations_meta: dict,
) -> pd.DataFrame:
    """Build a (lng, lat, value) DataFrame for a single pollutant.

    Parameters
    ----------
    annual_stats : pd.DataFrame
        Output of ``compute_annual_stats``.
    pollutant : str
        ``"PM2.5"`` or ``"PM10"`` or ``"NO2"``.
    stations_meta : dict
        ``STATIONS_META`` dict with keys matching station names.

    Returns
    -------
    pd.DataFrame with columns ``station_name``, ``lng``, ``lat``, ``value``.
    """
    subset = annual_stats[annual_stats["pollutant"] == pollutant].copy()
    rows = []
    for _, row in subset.iterrows():
        name = row["station_name"]
        meta = stations_meta.get(name)
        val = row["annual_mean"]
        if meta is None or val <= 0:
            continue  # skip missing/zero data
        rows.append({
            "station_name": name,
            "lng": meta["lng"],
            "lat": meta["lat"],
            "value": val,
        })
    return pd.DataFrame(rows)
