from __future__ import annotations

import sys
from pathlib import Path

import ee
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.aoi import get_periferia_zmvm_aoi
from src.config import EE_PROJECT_ID
from src.landsat import load_lst_composite, load_ndvi_composite
from src.sentinel5p import load_no2_composite
from src.stations import STATIONS_META


def main() -> None:
    ee.Initialize(project=EE_PROJECT_ID)

    aoi_fc = get_periferia_zmvm_aoi()
    n_feats = aoi_fc.size().getInfo()
    print(f"AOI loaded: {n_feats} features")

    print("Loading NDVI composite (summer 2025)...")
    ndvi_img = load_ndvi_composite(aoi_fc, "2025-06-01", "2025-09-01")
    ndvi_result = ndvi_img.reduceRegions(
        collection=aoi_fc, reducer=ee.Reducer.mean(), scale=30,
    )
    ndvi_map = {}
    for feat in ndvi_result.getInfo()["features"]:
        p = feat["properties"]
        ndvi_map[p.get("NOMGEO", "")] = p.get("mean", None)

    print("Loading LST composite (summer 2025)...")
    lst_img = load_lst_composite(aoi_fc, "2025-06-01", "2025-09-01")
    lst_result = lst_img.reduceRegions(
        collection=aoi_fc, reducer=ee.Reducer.mean(), scale=30,
    )
    lst_map = {}
    for feat in lst_result.getInfo()["features"]:
        p = feat["properties"]
        lst_map[p.get("NOMGEO", "")] = p.get("mean", None)

    print("Loading NO2 composite (2023)...")
    no2_img = load_no2_composite(aoi_fc, "2023-01-01", "2024-01-01")
    no2_result = no2_img.reduceRegions(
        collection=aoi_fc, reducer=ee.Reducer.mean(), scale=1000,
    )
    no2_map = {}
    for feat in no2_result.getInfo()["features"]:
        p = feat["properties"]
        no2_map[p.get("NOMGEO", "")] = p.get("mean", None)

    print("Merging PM2.5/PM10 from ground stations...")
    pm_path = PROJECT_ROOT / "data" / "processed" / "ground_stations_annual_2023.csv"
    st = pd.read_csv(pm_path)
    st = st[st["annual_mean"] > 0]

    station_to_municipio = {
        name: meta["municipio"] for name, meta in STATIONS_META.items()
    }
    st = st.copy()
    st["municipio"] = st["station_name"].map(station_to_municipio)

    municipio_names = sorted(ndvi_map.keys())
    pm_data = {}
    for mun in municipio_names:
        mun_st = st[st["municipio"] == mun]
        pm25 = mun_st[mun_st["pollutant"] == "PM2.5"]["annual_mean"]
        pm10 = mun_st[mun_st["pollutant"] == "PM10"]["annual_mean"]
        pm_data[mun] = {
            "pm25_mean": pm25.mean() if not pm25.empty else float("nan"),
            "pm10_mean": pm10.mean() if not pm10.empty else float("nan"),
        }

    rows = []
    for feat in ndvi_result.getInfo()["features"]:
        p = feat["properties"]
        name = p.get("NOMGEO", "")
        rows.append({
            "NOM_MUN": name,
            "CVE_ENT": p.get("CVE_ENT", ""),
            "CVE_MUN": p.get("CVE_MUN", ""),
            "lst_mean": lst_map.get(name),
            "ndvi_mean": ndvi_map.get(name),
            "no2_mean": no2_map.get(name),
            "pm25_mean": pm_data[name]["pm25_mean"],
            "pm10_mean": pm_data[name]["pm10_mean"],
        })

    df = pd.DataFrame(rows)
    print(df.to_string())

    out_path = PROJECT_ROOT / "data" / "processed" / "municipio_indicators.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
