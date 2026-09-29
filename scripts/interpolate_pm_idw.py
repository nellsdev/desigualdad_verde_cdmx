#!/usr/bin/env python3
"""Interpolate missing PM2.5 and PM10 values using Inverse Distance Weighting (IDW)
between municipio centroids.

Reads the existing municipio_indicators.csv, loads INEGI municipio shapefiles,
computes centroids, and fills NaN PM values via IDW (power=2, 5 nearest neighbors).
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PERIFERIA_ZMVM

# ── Paths ─────────────────────────────────────────────────────────────────────
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "municipio_indicators.csv"

CDMX_MUN_SHP = (
    PROJECT_ROOT
    / "data" / "raw" / "shapefiles" / "09_ciudaddemexico"
    / "conjunto_de_datos" / "09mun.shp"
)
EDOMEX_MUN_SHP = (
    PROJECT_ROOT
    / "data" / "raw" / "shapefiles" / "15_mexico"
    / "conjunto_de_datos" / "15mun.shp"
)

# All 21 municipios in the study area
ALL_MUNICIPIOS = [
    # CDMX (16)
    "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán",
    "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero",
    "Iztacalco", "Iztapalapa", "La Magdalena Contreras", "Miguel Hidalgo",
    "Milpa Alta", "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco",
    # EdoMex (5)
    "Nezahualcóyotl", "Ecatepec de Morelos", "Naucalpan de Juárez",
    "Tlalnepantla de Baz", "Coacalco de Berriozábal",
]


def load_municipio_centroids() -> gpd.GeoDataFrame:
    """Load the 21 study-area municipio shapefiles and return a
    GeoDataFrame with a centroid point for each."""
    cdmx = gpd.read_file(CDMX_MUN_SHP)
    edomex = gpd.read_file(EDOMEX_MUN_SHP)

    # Filter to only the study-area EdoMex municipios
    edomex_study = edomex[edomex["NOMGEO"].isin(PERIFERIA_ZMVM)].copy()

    gdf = pd.concat([cdmx, edomex_study], ignore_index=True)

    # Both shapefiles are in ITRF2008 / UTM zone 14N (EPSG:6372) — a
    # meter-based projection, perfect for distance calculations.
    # Keep in this CRS so distances are in meters.
    assert gdf.crs is not None, "Shapefile CRS is missing"

    centroids = gdf[["CVEGEO", "CVE_ENT", "CVE_MUN", "NOMGEO", "geometry"]].copy()
    centroids["centroid"] = centroids.geometry.centroid

    return centroids


def idw_interpolate(
    target_name: str,
    source_df: pd.DataFrame,
    centroids_gdf: gpd.GeoDataFrame,
    pollutant_col: str,
    n_neighbors: int = 5,
    power: float = 2.0,
    max_distance_m: float = 50_000.0,
) -> float:
    """Interpolate a single missing PM value using IDW.

    Parameters
    ----------
    target_name : str
        NOMGEO of the municipio to interpolate.
    source_df : pd.DataFrame
        DataFrame with NOM_MUN and pollutant_col columns for municipios
        that already have data.
    centroids_gdf : gpd.GeoDataFrame
        Centroids for all municipios (NOMGEO + centroid geometry).
    pollutant_col : str
        Column name to interpolate (e.g. 'pm25_mean').
    n_neighbors : int
        Number of nearest neighbors to use.
    power : float
        Distance decay exponent (default 2.0 for quadratic).
    max_distance_m : float
        Maximum distance in meters beyond which neighbors are ignored.

    Returns
    -------
    Interpolated value, or NaN if no valid neighbors.
    """
    target_centroid = centroids_gdf.loc[
        centroids_gdf["NOMGEO"] == target_name, "centroid"
    ].iloc[0]

    # Municipios with valid data for this pollutant
    source_muns = source_df.loc[
        source_df[pollutant_col].notna(), "NOM_MUN"
    ].values

    candidates: list[tuple[float, float]] = []  # (distance_m, value)
    for mun in source_muns:
        src_row = centroids_gdf.loc[centroids_gdf["NOMGEO"] == mun]
        if src_row.empty:
            continue
        src_centroid = src_row["centroid"].iloc[0]
        d = target_centroid.distance(src_centroid)
        if d <= 0:
            continue
        val = source_df.loc[source_df["NOM_MUN"] == mun, pollutant_col].iloc[0]
        if not np.isfinite(val):
            continue
        candidates.append((d, val))

    if not candidates:
        return float("nan")

    # Sort by distance, respect max distance, take nearest n
    candidates.sort(key=lambda x: x[0])
    candidates = [(d, v) for d, v in candidates if d <= max_distance_m]
    if not candidates:
        return float("nan")
    nearest = candidates[:n_neighbors]

    # IDW with power decay
    weights = np.array([1.0 / (d**power) for d, _ in nearest])
    values = np.array([v for _, v in nearest])
    w_sum = weights.sum()

    if w_sum <= 0:
        return float("nan")
    return float(np.average(values, weights=weights))


def main() -> None:
    print("=" * 60)
    print("IDW Interpolation of Missing PM Values")
    print("=" * 60)

    # ── 1. Load centroids ────────────────────────────────────────────────────
    print("\n[1/5] Loading municipio centroids from shapefiles...")
    centroids = load_municipio_centroids()
    print(f"       Loaded {len(centroids)} municipios in CRS: {centroids.crs}")

    # ── 2. Load current CSV ──────────────────────────────────────────────────
    print("\n[2/5] Loading current municipio_indicators.csv...")
    df = pd.read_csv(CSV_PATH)
    print(f"       {len(df)} rows loaded")

    # ── 3. Print before state ────────────────────────────────────────────────
    print(f"\n[3/5] Before interpolation:")
    for pol_col in ["pm25_mean", "pm10_mean"]:
        n_missing = df[pol_col].isna().sum()
        print(f"       {pol_col}: {n_missing} NaN out of {len(df)}")
        if n_missing > 0:
            missing_muns = df[df[pol_col].isna()]["NOM_MUN"].tolist()
            print(f"       Missing: {missing_muns}")

    # ── 4. Interpolate ──────────────────────────────────────────────────────
    print(f"\n[4/5] Running IDW interpolation (power=2, n_neighbors=5, max=50km)...")
    results: list[dict] = []
    for pol_col in ["pm25_mean", "pm10_mean"]:
        missing_muns = df[df[pol_col].isna()]["NOM_MUN"].values
        if len(missing_muns) == 0:
            print(f"       {pol_col}: no missing values, skipping")
            continue
        print(f"       {pol_col}: interpolating for {list(missing_muns)}")
        for mun in missing_muns:
            old_val = df.loc[df["NOM_MUN"] == mun, pol_col].iloc[0]
            new_val = idw_interpolate(mun, df, centroids, pol_col)
            df.loc[df["NOM_MUN"] == mun, pol_col] = new_val
            results.append({
                "NOM_MUN": mun,
                "pollutant": pol_col,
                "old_value": old_val,
                "new_value": new_val,
            })
            if np.isfinite(new_val):
                print(f"         {mun}: {old_val} → {new_val:.4f}")
            else:
                print(f"         {mun}: {old_val} → FAILED (no valid neighbors)")

    # ── 5. Save ──────────────────────────────────────────────────────────────
    print(f"\n[5/5] Saving to {CSV_PATH}...")
    df.to_csv(CSV_PATH, index=False)
    print("       Done.")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("Summary")
    print("=" * 60)
    for pol_col in ["pm25_mean", "pm10_mean"]:
        n_missing = df[pol_col].isna().sum()
        print(f"  {pol_col}: {n_missing} NaN remaining")
    print()

    print("Before / After comparison:")
    compar = df[["NOM_MUN", "pm25_mean", "pm10_mean"]].copy()
    compar.columns = ["Municipio", "PM2.5 (µg/m³)", "PM10 (µg/m³)"]
    print(compar.to_string(index=False))


if __name__ == "__main__":
    main()
