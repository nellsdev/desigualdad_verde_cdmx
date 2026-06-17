"""
Sprint 2 — Master DataFrame Pipeline.

Builds a single GeoDataFrame at the AGEB level for the Zona Metropolitana
del Valle de México (ZMVM) by merging:

    - INEGI AGEB boundaries (CDMX + EdoMex)
    - INEGI demographic characteristics (GeoJSON)
    - CONAPO marginalization index 2020 (IMU)
    - Atlas de Riesgo — temperaturas máximas
    - Áreas verdes urbanas (spatial join, CDMX only)

Usage::

    from src.data_pipeline import build_master_dataframe

    master = build_master_dataframe()
    master.to_file("data/processed/master_ageb_zmvm.gpkg", layer="master")
    master.to_csv("data/processed/master_ageb_zmvm.csv")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd

from .config import (
    PROJECT_ROOT,
    ZONE_METROPOLITANA_VALLE_MEXICO_EDOMEX_MUNS as ZMVM_EDOMEX_MUNS,
)

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────

SHAPEFILE_CDMX: Path = (
    PROJECT_ROOT / "data/raw/shapefiles/09_ciudaddemexico/conjunto_de_datos"
)
SHAPEFILE_EDOMEX: Path = (
    PROJECT_ROOT / "data/raw/shapefiles/15_mexico/conjunto_de_datos"
)

DEMOGRAFIA_PATH: Path = (
    PROJECT_ROOT / "data/raw/caractersticas-demogrficas-nivel-ageb.json"
)

CONAPO_PATH: Path = PROJECT_ROOT / "data/raw/IMU_2020_CDMX_EdoMex.csv"

ATLAS_TEMP_PATH: Path = (
    PROJECT_ROOT / "data/raw/atlas-de-riesgo-temperaturas-maximas.csv"
)

AREAS_VERDES_PATH: Path = (
    PROJECT_ROOT / "data/raw/shapefiles/areas_naturales/cdmx_areas_verdes_2017.csv"
)

DGIS_EGRESOS_PATH: Path = (
    PROJECT_ROOT / "data/raw/dgis/Registros/Egresos.txt"
)


# ──────────────────────────────────────────────────────────────────────────────
# Loaders
# ──────────────────────────────────────────────────────────────────────────────


def _load_ageb_boundaries() -> gpd.GeoDataFrame:
    """Load and concatenate urban AGEB shapefiles for CDMX and EdoMex."""
    cdmx = gpd.read_file(SHAPEFILE_CDMX / "09a.shp")
    cdmx["entidad"] = "CDMX"

    edomex = gpd.read_file(SHAPEFILE_EDOMEX / "15a.shp")
    edomex["entidad"] = "EdoMex"

    combined = pd.concat([cdmx, edomex], ignore_index=True)

    if combined.crs is None:
        combined = combined.set_crs(epsg=4326)
    combined = combined.to_crs(epsg=4326)

    # Build the full 13-char CVE_AGEB from the component columns.
    # INEGI format: CVE_ENT (2) + CVE_MUN (3) + CVE_LOC (4) + CVE_AGEB (4)
    for col in ["CVE_ENT", "CVE_MUN", "CVE_LOC", "CVE_AGEB"]:
        combined[col] = combined[col].astype(str).str.strip()
    combined["CVE_AGEB_full"] = (
        combined["CVE_ENT"]
        + combined["CVE_MUN"].str.zfill(3)
        + combined["CVE_LOC"].str.zfill(4)
        + combined["CVE_AGEB"]
    )

    return combined


def _load_demografia() -> gpd.GeoDataFrame:
    """Load INEGI demographic characteristics as a GeoDataFrame."""
    gdf = gpd.read_file(DEMOGRAFIA_PATH)
    gdf = gdf.to_crs(epsg=4326)

    # Parse the joining key — the AGEB field has 13 characters:
    # ENT(2) + MUN(3) + LOC(4) + AGEB(4)
    gdf["CVE_AGEB"] = gdf["ageb"].astype(str).str.strip()
    return gdf


def _load_conapo() -> pd.DataFrame:
    """Load CONAPO marginalization index 2020 (already filtered)."""
    df = pd.read_csv(CONAPO_PATH, dtype={"CVE_AGEB": str})
    df["CVE_AGEB"] = df["CVE_AGEB"].astype(str).str.strip()

    # Columns we care about for the analysis
    keep = [
        "CVE_AGEB", "ENT", "NOM_ENT", "MUN", "NOM_MUN",
        "POB_TOTAL",
        "SBASC",       # % 15+ sin educación básica
        "PSDSS",       # % sin derechohabiencia a salud
        "OVSDE",       # % sin drenaje
        "OVSAE",       # % sin agua entubada
        "OVPT",        # % piso de tierra
        "OVHAC",       # % hacinamiento
        "OVSREF",      # % sin refrigerador
        "OVSINT",      # % sin internet
        "OVSCEL",      # % sin celular
        "IM_2020",     # índice de marginación
        "GM_2020",     # grado (categórico)
        "IMN_2020",    # índice normalizado
    ]
    return df[keep]


def _load_atlas_temperatura() -> pd.DataFrame:
    """Load Atlas de Riesgo temperature data (CDMX AGEBs).

    Returns a deduplicated DataFrame — one row per AGEB.
    When multiple return periods exist, keeps the highest intensity.
    """
    df = pd.read_csv(ATLAS_TEMP_PATH)
    df["CVE_AGEB"] = df["cvegeo"].astype(str).str.strip()

    # Deduplicate: if an AGEB has multiple return periods, keep the max.
    cols_intensity = [c for c in ["intensidad", "intens_uni", "intens_num"] if c in df.columns]
    df = df.sort_values("intens_num", ascending=False).drop_duplicates(
        subset=["CVE_AGEB"], keep="first"
    )
    return df


def _load_areas_verdes() -> gpd.GeoDataFrame:
    """Load and parse green areas as a GeoDataFrame."""
    df = pd.read_csv(AREAS_VERDES_PATH)

    # Parse the geo_shape column (JSON multipolygon)
    import json

    geometries = []
    valid_rows = []
    for idx, row in df.iterrows():
        try:
            geom_dict = json.loads(row["geo_shape"])
            geom = gpd.GeoDataFrame.from_features(
                [{"type": "Feature", "geometry": geom_dict, "properties": {}}]
            ).geometry.iloc[0]
            geometries.append(geom)
            valid_rows.append(row)
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    green = gpd.GeoDataFrame(
        pd.DataFrame(valid_rows),
        geometry=geometries,
        crs="EPSG:4326",
    )
    return green


# ──────────────────────────────────────────────────────────────────────────────
# Health data loader (DGIS)
# ──────────────────────────────────────────────────────────────────────────────


def _load_dgis_health(health_year: int = 2023) -> pd.DataFrame:
    """Load and aggregate respiratory hospital discharges from DGIS.

    Reads Egresos.txt, filters for ICD-10 J00-J47 in ZMVM (CDMX + EdoMex),
    and aggregates counts and average stay by municipality.

    Returns
    -------
    pd.DataFrame
        Columns: CVE_MUN, egresos_resp, egresos_resp_h, egresos_resp_m,
        egresos_resp_estancia_prom
    """
    cols = {
        "ID": str,
        "AFECPRIN": str,
        "ENTIDAD": str,
        "MUNIC": str,
        "SEXO": str,
        "EDAD": str,
        "CVEEDAD": str,
        "DIAS_ESTA": str,
    }

    df = pd.read_csv(
        DGIS_EGRESOS_PATH,
        sep="|",
        encoding="utf-8-sig",
        dtype=cols,
        usecols=list(cols),
        low_memory=False,
    )

    icd10_j_pattern = r"J(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-7])"
    mask_resp = df["AFECPRIN"].str.match(icd10_j_pattern, na=False)
    df = df.loc[mask_resp]

    mask_zmvm = df["ENTIDAD"].isin(["09", "15"])
    df = df.loc[mask_zmvm]

    mask_mun = ~df["MUNIC"].isin(["99", "998", "999"])
    df = df.loc[mask_mun]

    df["CVE_MUN"] = df["ENTIDAD"] + df["MUNIC"].str.zfill(3)

    agg = df.groupby("CVE_MUN", as_index=False).agg(
        egresos_resp=("ID", "count"),
        egresos_resp_h=("SEXO", lambda s: (s == "1").sum()),
        egresos_resp_m=("SEXO", lambda s: (s == "2").sum()),
        egresos_resp_estancia_prom=(
            "DIAS_ESTA",
            lambda s: pd.to_numeric(s, errors="coerce").mean(),
        ),
    )

    return agg


# ──────────────────────────────────────────────────────────────────────────────
# Pipeline builder
# ──────────────────────────────────────────────────────────────────────────────


def build_master_dataframe(
    load_health: bool = False,
    health_year: int = 2023,
) -> gpd.GeoDataFrame:
    """
    Build the master AGEB-level DataFrame for the ZMVM.

    Parameters
    ----------
    load_health : bool, optional
        Whether to attempt loading health data (requires separate download).
    health_year : int, optional
        Year for health data (default 2023).

    Returns
    -------
    gpd.GeoDataFrame
        Master DataFrame with AGEB geometry and all merged variables.
    """
    print("=" * 60)
    print("Master DataFrame Pipeline — IslasCalor Sprint 2")
    print("=" * 60)

    # ── Step 1: AGEB boundaries ──────────────────────────────────────────
    print("\n[1/6] Loading AGEB boundaries...")
    ageb = _load_ageb_boundaries()
    print(f"       {len(ageb):,} AGEB features (CDMX + EdoMex)")

    # ── Step 2: Demographics ────────────────────────────────────────────
    print("[2/6] Loading demographic data...")
    demo = _load_demografia()
    print(f"       {len(demo):,} AGEB with demographic data")

    # Merge boundaries + demographics (ageb field = full 13-char key)
    master = ageb.merge(
        demo.rename(columns={"ageb": "CVE_AGEB_full"}),
        on="CVE_AGEB_full",
        how="left",
        suffixes=("", "_demo"),
    )
    print(f"       After merge: {len(master):,} features")

    # ── Step 3: CONAPO marginalization ──────────────────────────────────
    print("[3/6] Loading CONAPO marginalization index...")
    conapo = _load_conapo()
    print(f"       {len(conapo):,} AGEB with marginalization data")

    master = master.merge(
        conapo.rename(columns={"CVE_AGEB": "CVE_AGEB_full"}),
        on="CVE_AGEB_full",
        how="left",
        suffixes=("", "_conapo"),
    )
    print(f"       After merge: {len(master):,} features")

    # ── Step 4: Atlas de Riesgo temperature ─────────────────────────────
    print("[4/6] Loading Atlas de Riesgo temperature data...")
    atlas = _load_atlas_temperatura()
    # Only for CDMX AGEBs — merge by cvegeo
    atlas_cols = ["CVE_AGEB_full", "intensidad", "intens_uni", "intens_num"]
    atlas = atlas.rename(columns={"CVE_AGEB": "CVE_AGEB_full"})
    existing = [c for c in atlas_cols if c in atlas.columns]
    master = master.merge(atlas[existing], on="CVE_AGEB_full", how="left")
    print(f"       {atlas['CVE_AGEB_full'].nunique():,} AGEB with temperature data")

    # ── Step 5: Áreas verdes (spatial join, CDMX only) ──────────────────
    print("[5/6] Spatial join: green areas...")
    green = _load_areas_verdes()
    print(f"       {len(green):,} green area polygons")

    # Spatial join: sum green area per AGEB
    green_per_ageb = (
        gpd.sjoin(
            green,
            master[["CVE_AGEB_full", "geometry"]],
            how="inner",
            predicate="intersects",
        )
        .groupby("CVE_AGEB_full")
        .agg(
            area_verde_total_m2=("superficie", "sum"),
            num_areas_verdes=("superficie", "count"),
        )
        .reset_index()
    )
    master = master.merge(green_per_ageb, on="CVE_AGEB_full", how="left")
    master["area_verde_total_m2"] = master["area_verde_total_m2"].fillna(0)
    master["num_areas_verdes"] = master["num_areas_verdes"].fillna(0)
    print(f"       {green_per_ageb['CVE_AGEB_full'].nunique():,} AGEB con áreas verdes")

    # ── Step 6: DGIS health data ────────────────────────────────────────
    health_cols_counts = ["egresos_resp", "egresos_resp_h", "egresos_resp_m"]
    if load_health:
        print("[6/6] Loading DGIS respiratory health data...")
        health = _load_dgis_health(health_year=health_year)
        print(f"       {len(health):,} municipalities with respiratory cases")

        master["CVE_MUN_key"] = master["CVE_ENT"] + master["CVE_MUN"].str.zfill(3)
        master = master.merge(health, left_on="CVE_MUN_key", right_on="CVE_MUN", how="left", suffixes=("", "_health"))

        for c in health_cols_counts:
            master[c] = master[c].fillna(0).astype(int)
        master["egresos_resp_estancia_prom"] = master["egresos_resp_estancia_prom"].fillna(0)

        master = master.drop(columns=["CVE_MUN_key", "CVE_MUN_health"])
        print(f"       Total respiratory cases in ZMVM: {master['egresos_resp'].sum():,}")
    else:
        print("[6/6] Skipping health data (set load_health=True to include)")
        for c in health_cols_counts + ["egresos_resp_estancia_prom"]:
            master[c] = 0
        print(f"       {len(master):,} features (health columns zero-filled)")

    # ── Summary ─────────────────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print(f"Master DataFrame: {len(master):,} AGEB features")
    print(f"Columns: {len(master.columns)}")
    print(f"Geometry: {master.geometry.name}")
    print(f"{'─' * 60}")

    return master


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build master AGEB DataFrame for ZMVM")
    parser.add_argument(
        "--load-health",
        action="store_true",
        help="Load DGIS respiratory health data",
    )
    args = parser.parse_args()

    master = build_master_dataframe(load_health=args.load_health)

    out_dir = PROJECT_ROOT / "data/processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Drop extra geometry columns from merge (keep only the active one)
    geom_cols = [c for c in master.columns if hasattr(master[c], "dtype") and master[c].dtype.name == "geometry"]
    for c in geom_cols[1:]:
        master = master.drop(columns=[c])

    # Save as GeoPackage
    gpkg_path = out_dir / "master_ageb_zmvm.gpkg"
    master.to_file(gpkg_path, layer="master", driver="GPKG")
    print(f"\nSaved: {gpkg_path}")

    # Save as CSV (drop geometry)
    csv_path = out_dir / "master_ageb_zmvm.csv"
    master.drop(columns=[master.geometry.name]).to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")
