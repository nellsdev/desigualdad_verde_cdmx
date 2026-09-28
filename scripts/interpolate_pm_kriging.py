#!/usr/bin/env python3
"""Interpolate missing PM2.5 and PM10 values using Ordinary Kriging (PyKrige).

Reads the existing municipio_indicators.csv, loads INEGI municipio shapefiles,
computes centroids, and fills NaN PM values via Ordinary Kriging using
station monitor data from ground_stations_annual_2023.csv.

Station coordinates are in WGS84 (EPSG:4326, decimal degrees). Shapefiles are
in ITRF2008 / UTM zone 14N (EPSG:6372, meters). Centroids are converted to
WGS84 before kriging so all coordinate systems are consistent.

Requires: pykrige, geopandas, numpy, pandas.
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pykrige.ok import OrdinaryKriging

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.interpolation import prepare_station_data
from src.config import PERIFERIA_ZMVM
from src.stations import STATIONS_META

# ── Paths ─────────────────────────────────────────────────────────────────────
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "municipio_indicators.csv"
STN_PATH = PROJECT_ROOT / "data" / "processed" / "ground_stations_annual_2023.csv"
CDMX_SHP = (
    PROJECT_ROOT
    / "data" / "raw" / "shapefiles" / "09_ciudaddemexico"
    / "conjunto_de_datos" / "09mun.shp"
)
EDOMEX_SHP = (
    PROJECT_ROOT
    / "data" / "raw" / "shapefiles" / "15_mexico"
    / "conjunto_de_datos" / "15mun.shp"
)

# ── Configuration ─────────────────────────────────────────────────────────────
VARIOCRAM_MODEL: str = "spherical"
"""Variogram model passed to PyKrige's OrdinaryKriging."""

# The four municipios that originally had NaN PM values (filled by the IDW
# script, now to be replaced by kriging estimates).
TARGET_MUNICIPIOS: list[str] = [
    "Venustiano Carranza",
    "La Magdalena Contreras",
    "Ecatepec de Morelos",
    "Miguel Hidalgo",
]

# Minimum valid annual mean (µg/m³) — stations below this are considered
# non-functional for that pollutant (e.g. Miguel Hidalgo station reports
# 0.002 for PM2.5 and 0.007 for PM10, which are effectively "no data").
MIN_VALID_PM: float = 1.0

# UTM zone 14N CRS (ITRF2008 / UTM zone 14N = EPSG:6372) — consistent with
# the shapefiles. Kriging in meter-based coordinates avoids numerical issues
# from tiny degree-scale distances.
UTM_CRS: str = "EPSG:6372"

# WGS84 lat/lng bounds for CDMX metro area — used to sanity-check centroids.
LNG_MIN, LNG_MAX = -99.4, -98.9
LAT_MIN, LAT_MAX = 19.1, 19.7


# ── Helpers ───────────────────────────────────────────────────────────────────


def load_municipio_centroids_wgs84() -> gpd.GeoDataFrame:
    """Load the 21 study-area municipios and return centroids in WGS84.

    Steps
    -----
    1. Read CDMX (16 alcaldías) and EdoMex (5 periferia) shapefiles.
    2. Compute polygon centroids in native CRS (EPSG:6372, UTM meters).
    3. Reproject centroids to EPSG:4326 (WGS84 decimal degrees).

    Returns
    -------
    GeoDataFrame with columns ``NOMGEO``, ``cx`` (lng), ``cy`` (lat).
    """
    cdmx = gpd.read_file(CDMX_SHP)
    edomex = gpd.read_file(EDOMEX_SHP)

    # Keep only the 5 EdoMex municipios that are part of the study area
    edomex_study = edomex[edomex["NOMGEO"].isin(PERIFERIA_ZMVM)].copy()

    gdf = pd.concat([cdmx, edomex_study], ignore_index=True)
    assert gdf.crs is not None, f"Shapefile CRS is missing (got {gdf.crs})"

    # Centroids in native CRS (UTM meters), then convert to WGS84 degrees
    centroids = gdf[["CVEGEO", "CVE_ENT", "CVE_MUN", "NOMGEO", "geometry"]].copy()
    centroids["centroid"] = centroids.geometry.centroid
    centroids = centroids.set_geometry("centroid", crs=gdf.crs)
    centroids = centroids.to_crs("EPSG:4326")

    centroids["cx"] = centroids.geometry.x  # longitude
    centroids["cy"] = centroids.geometry.y  # latitude

    return centroids


def coords_to_utm(
    lngs: np.ndarray,
    lats: np.ndarray,
    src_crs: str = "EPSG:4326",
    dst_crs: str = UTM_CRS,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert arrays of (lng, lat) to UTM (easting, northing)."""
    import geopandas as gpd
    from shapely.geometry import Point

    points = [Point(x, y) for x, y in zip(lngs, lats)]
    gdf = gpd.GeoDataFrame(geometry=points, crs=src_crs)
    gdf = gdf.to_crs(dst_crs)
    xs = gdf.geometry.x.values
    ys = gdf.geometry.y.values
    return xs, ys


def krige_predict_at_points(
    stn_xs: np.ndarray,
    stn_ys: np.ndarray,
    stn_vals: np.ndarray,
    target_xs: np.ndarray,
    target_ys: np.ndarray,
    variogram_model: str = VARIOCRAM_MODEL,
) -> tuple[np.ndarray, np.ndarray]:
    """Run Ordinary Kriging at target point locations (all in same CRS / units).

    Parameters
    ----------
    stn_xs, stn_ys : 1-D arrays
        Station x/y coordinates (e.g. UTM easting/northing in meters).
    stn_vals : 1-D array
        Observed values at stations.
    target_xs, target_ys : 1-D arrays
        Prediction point coordinates (same CRS as stations).
    variogram_model : str
        Variogram model name (default ``"spherical"``).

    Returns
    -------
    z_pred : 1-D array of kriged estimates.
    sigma : 1-D array of kriging standard deviations.
    """
    ok = OrdinaryKriging(
        stn_xs,
        stn_ys,
        stn_vals,
        variogram_model=variogram_model,
        verbose=False,
        enable_plotting=False,
        # Small pseudo-nugget to stabilise the kriging matrix when stations
        # are very close together (common in CDMX's dense network).
        pseudo_inv=True,
    )
    z, sigma = ok.execute("points", target_xs, target_ys)

    z_pred = np.asarray(z).flatten()
    if sigma is not None:
        sigma_out = np.asarray(sigma).flatten()
    else:
        sigma_out = np.full_like(z_pred, np.nan)

    return z_pred, sigma_out


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    print("=" * 66)
    print("  Ordinary Kriging — Interpolation of Missing PM Values")
    print(f"  Variogram model: {VARIOCRAM_MODEL}")
    print("=" * 66)

    # ── 1. Load centroids ─────────────────────────────────────────────────────
    print("\n[1/5] Loading municipio centroids (EPSG:4326)...")
    centroids = load_municipio_centroids_wgs84()
    print(f"       → {len(centroids)} municipios loaded")

    # Verify target centroids are within reasonable bounds
    for mun in TARGET_MUNICIPIOS:
        row = centroids[centroids["NOMGEO"] == mun]
        if row.empty:
            print(f"       ⚠  {mun}: centroid NOT FOUND in shapefile")
        else:
            cx, cy = row["cx"].iloc[0], row["cy"].iloc[0]
            ok_lng = LNG_MIN <= cx <= LNG_MAX
            ok_lat = LAT_MIN <= cy <= LAT_MAX
            print(f"       ✓ {mun:<30s}  ({cx:.4f}, {cy:.4f}){'  ⚠ out of bounds' if not (ok_lng and ok_lat) else ''}")

    # ── 2. Load station data ──────────────────────────────────────────────────
    print("\n[2/5] Loading station annual stats...")
    annual_stats = pd.read_csv(STN_PATH)
    print(f"       → {len(annual_stats)} records ({annual_stats['station_name'].nunique()} stations × {annual_stats['pollutant'].nunique()} pollutants)")

    # ── 3. Show current CSV state (before) ────────────────────────────────────
    print("\n[3/5] Current municipio_indicators.csv (BEFORE kriging):")
    df = pd.read_csv(CSV_PATH)
    print(f"       → {len(df)} municipios")

    for pol_col, pol_name in [("pm25_mean", "PM2.5"), ("pm10_mean", "PM10")]:
        n_missing = int(df[pol_col].isna().sum())
        vals = df[pol_col].dropna()
        print(f"       {pol_col:>10s} ({pol_name}): {n_missing} NaN, "
              f"{len(vals)} valid  [{vals.min():.2f} – {vals.max():.2f}]")

    # Print the 4 target rows before
    print("\n       Target municipios (current, from IDW):")
    target_before = df[df["NOM_MUN"].isin(TARGET_MUNICIPIOS)][
        ["NOM_MUN", "pm25_mean", "pm10_mean"]
    ].copy()
    for _, r in target_before.iterrows():
        print(f"         {r['NOM_MUN']:<30s}  PM2.5={r['pm25_mean']:>8.4f}  PM10={r['pm10_mean']:>8.4f}")

    # ── 4. Kriging interpolation ─────────────────────────────────────────────
    print(f"\n[4/5] Running Ordinary Kriging ({VARIOCRAM_MODEL})...")

    all_results: list[dict] = []

    for pol_col, pol_name in [("pm25_mean", "PM2.5"), ("pm10_mean", "PM10")]:

        # --- 4a. Prepare station data ---
        stn_df = prepare_station_data(annual_stats, pol_name, STATIONS_META)
        if stn_df.empty:
            print(f"\n       {pol_name}: ⚠ NO valid station data — skipping")
            continue

        # Filter out stations with physically implausible near-zero values
        # (monitors that had no valid readings for that pollutant in 2023).
        n_before = len(stn_df)
        stn_df = stn_df[stn_df["value"] >= MIN_VALID_PM].copy()
        n_filtered = n_before - len(stn_df)

        if stn_df.empty:
            print(f"\n       {pol_name}: ⚠ All {n_before} stations filtered out (value < {MIN_VALID_PM})")
            continue

        print(f"\n       ── {pol_name} ({pol_col}) ──")
        print(f"       Stations ({len(stn_df)} + {n_filtered} filtered): {', '.join(stn_df['station_name'].tolist())}")
        print(f"       Value range: {stn_df['value'].min():.4f} – {stn_df['value'].max():.4f}")

        # --- 4b. Gather target coordinates (WGS84) ---
        target_rows = centroids[centroids["NOMGEO"].isin(TARGET_MUNICIPIOS)]
        found_muns = target_rows["NOMGEO"].tolist()
        target_lngs = target_rows["cx"].values.astype(float)
        target_lats = target_rows["cy"].values.astype(float)

        if len(found_muns) == 0:
            print(f"       ⚠ No target municipios found in centroids — skipping")
            continue

        if len(found_muns) < len(TARGET_MUNICIPIOS):
            missing = set(TARGET_MUNICIPIOS) - set(found_muns)
            print(f"       ⚠ Missing centroids for: {missing}")

        # --- 4c. Convert station & target coords to UTM (meters) ---
        # Kriging in UTM avoids numerical issues from tiny degree-scale
        # distances, giving the variogram physically meaningful lag distances.
        station_east, station_north = coords_to_utm(
            stn_df["lng"].values.astype(float),
            stn_df["lat"].values.astype(float),
        )
        target_east, target_north = coords_to_utm(target_lngs, target_lats)
        station_vals = stn_df["value"].values.astype(float)

        # --- 4d. Run kriging in UTM ---
        z_pred, sigma_pred = krige_predict_at_points(
            station_east, station_north, station_vals,
            target_east, target_north,
            variogram_model=VARIOCRAM_MODEL,
        )

        # --- 4e. Update CSV and record results ---
        for mun, pred_val, pred_sigma in zip(found_muns, z_pred, sigma_pred):
            match_idx = df.index[df["NOM_MUN"] == mun]
            if len(match_idx) == 0:
                print(f"       {mun:<30s}: NOT in CSV — skipping")
                continue

            old_val = df.at[match_idx[0], pol_col]
            df.at[match_idx[0], pol_col] = pred_val

            all_results.append({
                "NOM_MUN": mun,
                "pollutant": pol_name,
                "col": pol_col,
                "old_value": old_val,
                "new_value": pred_val,
                "sigma": pred_sigma,
            })

            # Show distance from nearest station as context
            dx = station_east - target_east[found_muns.index(mun)]
            dy = station_north - target_north[found_muns.index(mun)]
            dists_km = np.sqrt(dx**2 + dy**2) / 1000.0
            nearest_km = float(dists_km.min())

            print(f"       {mun:<30s}: {old_val:>8.4f} → {pred_val:>8.4f}  "
                  f"(σ={pred_sigma:.4f}, nearest_stn={nearest_km:.1f}km)")

    # ── 5. Save ───────────────────────────────────────────────────────────────
    print(f"\n[5/5] Saving updated CSV → {CSV_PATH}")
    df.to_csv(CSV_PATH, index=False)
    print("       ✓ Done.")

    # ── Final Summary ─────────────────────────────────────────────────────────
    print(f"\n{'=' * 66}")
    print("  Final Summary")
    print("=" * 66)

    for pol_col, pol_name in [("pm25_mean", "PM2.5"), ("pm10_mean", "PM10")]:
        n_missing = int(df[pol_col].isna().sum())
        vals = df[pol_col].dropna()
        print(f"  {pol_name:>5s} ({pol_col}): {n_missing} NaN, "
              f"{len(vals)} valid  [{vals.min():.2f} – {vals.max():.2f}]")

    print(f"\n  {'─'*60}")
    print(f"  {'Municipio':<30s} {'PM2.5 Before':>12s} {'PM2.5 After':>12s} {'PM10 Before':>12s} {'PM10 After':>12s}")
    print(f"  {'─'*60}")

    # Build before/after table for all 21 municipios
    for _, row in df.iterrows():
        mun = row["NOM_MUN"]
        pm25 = row["pm25_mean"]
        pm10 = row["pm10_mean"]
        # Find old values from results
        old_pm25 = next((r["old_value"] for r in all_results
                         if r["NOM_MUN"] == mun and r["col"] == "pm25_mean"), pm25)
        old_pm10 = next((r["old_value"] for r in all_results
                         if r["NOM_MUN"] == mun and r["col"] == "pm10_mean"), pm10)
        marker = " ◀" if mun in TARGET_MUNICIPIOS else ""
        print(f"  {mun:<30s} {old_pm25:>12.4f} {pm25:>12.4f} {old_pm10:>12.4f} {pm10:>12.4f}{marker}")

    # Detailed kriging results with sigma
    if all_results:
        print(f"\n  Kriging Details (with standard deviations):")
        print(f"  {'─'*66}")
        print(f"  {'Municipio':<30s} {'Pollutant':>8s} {'Old':>10s} {'New':>10s} {'σ':>8s} {'95% CI':>16s}")
        print(f"  {'─'*66}")
        for r in all_results:
            ci_lo = r["new_value"] - 1.96 * r["sigma"]
            ci_hi = r["new_value"] + 1.96 * r["sigma"]
            print(f"  {r['NOM_MUN']:<30s} {r['pollutant']:>8s} {r['old_value']:>10.4f} "
                  f"{r['new_value']:>10.4f} {r['sigma']:>8.4f} [{ci_lo:>7.2f}, {ci_hi:>7.2f}]")

    print(f"\n{'=' * 66}")


if __name__ == "__main__":
    main()
