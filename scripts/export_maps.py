"""Export static PNG maps and charts for social media — IslasCalor project.

Three sets of outputs:
  - *_<region>.png       : Municipio-level choropleth maps with state background
  - *_chart_zmvm.png     : Bar/column charts for data comparison
  - pm*/no2_zmvm.png     : Kriging-interpolated surface maps from station data

Output subdirectories:
  - zmvm/         : Full ZMVM choropleths, charts, and interpolated surfaces
  - cdmx/         : CDMX-only maps
  - incidencia/   : Zoomed incidencia-corridor maps (CDMX + norte EdoMex)
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

# -- paths
PROJ = Path(__file__).resolve().parents[1]
DATA = PROJ / "data"
OUT = PROJ / "outputs" / "mapas"
OUT.mkdir(parents=True, exist_ok=True)

CDMX_SHP = DATA / "raw" / "shapefiles" / "09_ciudaddemexico" / "conjunto_de_datos" / "09ent.shp"
EDOMEX_SHP = DATA / "raw" / "shapefiles" / "15_mexico" / "conjunto_de_datos" / "15ent.shp"
CDMX_MUN_SHP = DATA / "raw" / "shapefiles" / "09_ciudaddemexico" / "conjunto_de_datos" / "09mun.shp"
EDOMEX_MUN_SHP = DATA / "raw" / "shapefiles" / "15_mexico" / "conjunto_de_datos" / "15mun.shp"

# -- ZMVM municipios: 16 CDMX alcaldías + 60 EdoMex
CDMX_ALCALDIAS = frozenset({
    "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán",
    "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero",
    "Iztacalco", "Iztapalapa", "La Magdalena Contreras", "Miguel Hidalgo",
    "Milpa Alta", "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco",
})
EDOMEX_ZMVM = frozenset({
    "Acolman", "Amecameca", "Apaxco", "Atenco", "Atizapán de Zaragoza",
    "Atlautla", "Axapusco", "Ayapango", "Coacalco de Berriozábal",
    "Cocotitlán", "Coyotepec", "Cuautitlán", "Cuautitlán Izcalli", "Chalco",
    "Chiautla", "Chicoloapan", "Chiconcuac", "Chimalhuacán",
    "Ecatepec de Morelos", "Ecatzingo", "Huehuetoca", "Hueypoxtla",
    "Huixquilucan", "Isidro Fabela", "Ixtapaluca", "Jaltenco", "Jilotzingo",
    "Juchitepec", "La Paz", "Lerma", "Melchor Ocampo", "Naucalpan de Juárez",
    "Nextlalpan", "Nezahualcóyotl", "Nicolás Romero", "Nopaltepec",
    "Ocoyoacac", "Otumba", "Ozumba", "Papalotla",
    "San Martín de las Pirámides", "Tecámac", "Temamatla", "Temascalapa",
    "Tenango del Aire", "Tenango del Valle", "Teoloyucan", "Tepetlaoxtoc",
    "Tepetlixpa", "Tepotzotlán", "Tequixquiac", "Texcoco", "Tezoyuca",
    "Tlalmanalco", "Tlalnepantla de Baz", "Tultepec", "Tultitlán",
    "Valle de Chalco Solidaridad", "Villa del Carbón", "Zumpango",
})
ZMVM_MUNS = CDMX_ALCALDIAS | EDOMEX_ZMVM

# -- zone definitions
NORTE_MUNS = frozenset({
    "Gustavo A. Madero", "Iztapalapa",
    "Tlalnepantla de Baz", "Naucalpan de Juárez",
    "Ecatepec de Morelos", "Nezahualcóyotl",
})
SUR_MUNS = frozenset({
    "Coyoacán", "Álvaro Obregón", "Tlalpan",
    "La Magdalena Contreras", "Cuajimalpa de Morelos", "Xochimilco",
})

# -- zona de incidencia del colectivo
ZONA_INCIDENCIA = frozenset({"Ecatepec de Morelos", "Gustavo A. Madero", "Nezahualcóyotl"})
INC_EC = "#FFD700"
INC_LW = 3.0

COLORS = {"norte": "#E63946", "centro": "#F4A261", "sur": "#2A9D8F", "periferia": "#8B8B8B"}
ZONE_LABELS = {"norte": "Norte (nororiente)", "centro": "Centro (CDMX)", "sur": "Sur (referencia)", "periferia": "Periferia (EdoMex)"}
INC_LABELS = {**ZONE_LABELS, "norte": "Incidencia"}

# -- leyendas descriptivas por variable
LST_LABELS = {
    "norte": "Norte — más calor (~35°C)",
    "centro": "Centro — templado (~34°C)",
    "sur": "Sur — más fresco (~28.5°C)",
    "periferia": "Periferia (EdoMex)",
}
INC_LST_LABELS = {**LST_LABELS, "norte": "Incidencia — más calor (~35°C)"}

NDVI_LABELS = {
    "norte": "Norte — poca vegetación (NDVI 0.12)",
    "centro": "Centro — veg. media (NDVI 0.20)",
    "sur": "Sur — más vegetación (NDVI 0.33)",
    "periferia": "Periferia (EdoMex)",
}
INC_NDVI_LABELS = {**NDVI_LABELS, "norte": "Incidencia — poca vegetación (NDVI 0.12)"}

NO2_LABELS = {
    "norte": "Norte — más contaminado",
    "centro": "Centro — contaminación media",
    "sur": "Sur — menos contaminado",
    "periferia": "Periferia (EdoMex)",
}
INC_NO2_LABELS = {**NO2_LABELS, "norte": "Incidencia — más contaminado"}

ZONE_ORDER = ["norte", "centro", "sur", "periferia"]

# -- region split
REGION_TITLES = {"zmvm": "ZMVM", "cdmx": "CDMX", "edomex": "EdoMex"}
REGION_FILES = {"zmvm": "zmvm", "cdmx": "cdmx", "edomex": "edomex"}
REGION_DIRS = {"zmvm": "zmvm", "cdmx": "cdmx", "edomex": "incidencia"}
REGION_CVE = {"zmvm": None, "cdmx": "09", "edomex": "15"}


def _filter_region(mun_gdf: gpd.GeoDataFrame, sub_region: str) -> gpd.GeoDataFrame:
    """Filter municipio GDF to one entity, or return full ZMVM."""
    cve = REGION_CVE[sub_region]
    if cve is None:
        return mun_gdf
    return mun_gdf[mun_gdf["CVE_ENT"] == cve].copy()


def _highlight_incidencia(ax, mun_gdf):
    """Draw a thick gold border around Ecatepec, GAM, Nezahualcóyotl."""
    subset = mun_gdf[mun_gdf["municipio"].isin(ZONA_INCIDENCIA)]
    if len(subset) > 0:
        subset.plot(ax=ax, facecolor="none", edgecolor=INC_EC, linewidth=INC_LW)


# -- figure config
DPI = 150
FIG_SIZE = (1080 / DPI, 1080 / DPI)
CREDIT = "Fuente: Landsat 8-9 / Sentinel-5P / SINAICA / CONAPO / INEGI"
TITLE_COLOR = "#1a1a2e"
GRAY_BG = "#e8e8e8"
UNSHADED_FILL = "#d8d8d8"
MUN_EC = "#ffffff"
MUN_LW = 0.4
ZMVM_EC = "#333333"
ZMVM_LW = 2
PAD = 0.02


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_state_bg() -> gpd.GeoDataFrame:
    cdmx = gpd.read_file(str(CDMX_SHP)).to_crs("EPSG:4326")
    edomex = gpd.read_file(str(EDOMEX_SHP)).to_crs("EPSG:4326")
    return pd.concat([cdmx, edomex], ignore_index=True)


def _load_municipios() -> gpd.GeoDataFrame:
    # 1. Full municipio boundaries (complete territory, not just urban)
    cdmx = gpd.read_file(str(CDMX_MUN_SHP)).to_crs("EPSG:4326")
    edomex = gpd.read_file(str(EDOMEX_MUN_SHP)).to_crs("EPSG:4326")
    full = pd.concat([cdmx, edomex], ignore_index=True)
    full = full.rename(columns={"NOMGEO": "municipio"})

    # Keep only ZMVM municipios (16 CDMX + 60 EdoMex)
    full = full[full["municipio"].isin(ZMVM_MUNS)].copy()

    # 2. Urban-only data from the analyzed AGEB GPKG
    ageb = gpd.read_file(str(DATA / "processed" / "master_ageb_zmvm.gpkg"))
    ageb = ageb.dropna(subset=["NOM_MUN"]).copy()
    ageb = ageb[ageb["NOM_MUN"].isin(ZMVM_MUNS)].copy()

    agg = {
        "CVE_ENT": "first",
        "CVE_MUN": "first",
        "GM_2020": lambda x: x.mode().iloc[0] if not x.mode().empty else None,
        "IM_2020": "mean",
        "area_verde_total_m2": "sum",
    }
    urban = ageb.dissolve(by="NOM_MUN", aggfunc=agg).reset_index()
    urban = urban.rename(columns={"NOM_MUN": "municipio"})

    # 3. Merge urban data onto full municipio shapes
    full = full.merge(
        urban[["municipio", "CVE_ENT", "CVE_MUN", "GM_2020", "IM_2020", "area_verde_total_m2"]],
        on="municipio",
        how="left",
        suffixes=("", "_urban"),
    )

    # 4. Assign zones
    full["zone"] = "periferia"
    norte = full["municipio"].isin(NORTE_MUNS)
    sur = full["municipio"].isin(SUR_MUNS)
    full.loc[norte, "zone"] = "norte"
    full.loc[sur, "zone"] = "sur"
    full.loc[(full["CVE_ENT"] == "09") & ~norte & ~sur, "zone"] = "centro"

    return full[["municipio", "CVE_ENT", "CVE_MUN", "GM_2020", "IM_2020", "area_verde_total_m2", "zone", "geometry"]]


def _zmvm_boundary(mun_gdf: gpd.GeoDataFrame) -> gpd.GeoSeries:
    return mun_gdf.dissolve().boundary


def _state_boundary(state_bg: gpd.GeoDataFrame, cve_ent: str) -> gpd.GeoSeries:
    """Boundary of a single state (CDMX or EdoMex) from the background GDF."""
    return state_bg[state_bg["CVE_ENT"] == cve_ent].dissolve().boundary


def _boundary_for(mun_gdf, state_bg, sub_region):
    """Return boundary: CDMX state polygon for cdmx maps, ZMVM boundary otherwise."""
    if sub_region == "cdmx":
        return _state_boundary(state_bg, "09")
    return _zmvm_boundary(mun_gdf)


def _plot_extent(ax, mun_gdf):
    b = mun_gdf.total_bounds
    dx = (b[2] - b[0]) * PAD
    dy = (b[3] - b[1]) * PAD
    ax.set_xlim(b[0] - dx, b[2] + dx)
    ax.set_ylim(b[1] - dy, b[3] + dy)


# Bounding box para maps de EdoMex — enfocado en el nororiente
# (Ecatepec, Neza, GAM + periferia cercana)
EDOMEX_BBOX = (-99.50, -98.88, 19.20, 19.75)


def _zoom_edomex(ax):
    """Recorta la vista al nororiente del EdoMex para los mapas estatales."""
    ax.set_xlim(EDOMEX_BBOX[0], EDOMEX_BBOX[1])
    ax.set_ylim(EDOMEX_BBOX[2], EDOMEX_BBOX[3])


def _zone_handles(present_zones=None, custom_labels=None):
    labels = custom_labels or ZONE_LABELS
    if present_zones is None:
        present_zones = set(ZONE_ORDER)
    return [Patch(facecolor=COLORS[z], label=labels[z]) for z in ZONE_ORDER if z in present_zones]


def _prepare_mun(mun_gdf, state_bg, sub_region):
    """Return (mun, boundary, labels, full) según sub_region.

    - zmvm : todo el ZMVM, boundary ZMVM, labels normales.
    - cdmx : solo CDMX, boundary CDMX, labels normales.
    - edomex : todo el ZMVM (data visible en ambas entidades),
               boundary ZMVM, labels con "norte"→"Incidencia",
               zoom al nororiente.
    Nunca se dibuja referencia unshaded — el state_bg gris da contexto suficiente.
    """
    if sub_region == "edomex":
        return mun_gdf, _zmvm_boundary(mun_gdf), INC_LABELS, None
    mun = _filter_region(mun_gdf, sub_region)
    boundary = _boundary_for(mun_gdf, state_bg, sub_region)
    return mun, boundary, ZONE_LABELS, None


def _style_map_ax(ax, title):
    ax.set_title(title, fontsize=13, fontweight="bold", color=TITLE_COLOR, pad=12)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[:].set_visible(False)


def _add_anno(ax, text, x, y, color):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=8,
            fontweight="bold", color=color, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color, linewidth=1.5))


def _save(fig, name):
    # Route to subfolder based on filename suffix
    if "_cdmx." in name:
        subdir = "cdmx"
    elif "_edomex." in name:
        subdir = "incidencia"
    elif "_zmvm." in name:
        subdir = "zmvm"
    else:
        subdir = ""
    path = (OUT / subdir / name) if subdir else (OUT / name)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.15, facecolor="white")
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.15, facecolor="white")
    plt.close(fig)
    print(f"  ✓ {path}")


def _credit(fig, text=None):
    fig.text(0.5, 0.008, text or CREDIT, ha="center", va="bottom", fontsize=7, color="#666666")


# ---------------------------------------------------------------------------
# 1-3: Zone choropleths
# ---------------------------------------------------------------------------

def _zone_map_base(ax, state_bg, mun_gdf, boundary, full_mun_gdf=None):
    state_bg.plot(ax=ax, color=GRAY_BG, edgecolor="none")
    # Full ZMVM as unshaded reference when in sub-region mode
    ref_gdf = full_mun_gdf if full_mun_gdf is not None else mun_gdf
    if full_mun_gdf is not None:
        full_mun_gdf.plot(ax=ax, color=UNSHADED_FILL, edgecolor=MUN_EC, linewidth=0.6)
    for z in ZONE_ORDER:
        subset = mun_gdf[mun_gdf["zone"] == z]
        if len(subset) > 0:
            subset.plot(ax=ax, color=COLORS[z], linewidth=MUN_LW, edgecolor=MUN_EC)
    boundary.plot(ax=ax, color=ZMVM_EC, linewidth=ZMVM_LW)
    _plot_extent(ax, ref_gdf)


def plot_lst(mun_gdf, state_bg, sub_region="zmvm"):
    mun, boundary, labels, full = _prepare_mun(mun_gdf, state_bg, sub_region)
    present = set(mun["zone"].unique())

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    _zone_map_base(ax, state_bg, mun, boundary, full_mun_gdf=full)
    _highlight_incidencia(ax, mun)
    if sub_region == "edomex":
        _zoom_edomex(ax)
    zone_name = "Incidencia" if sub_region == "edomex" else "Norte"
    for zone, (text, x, y) in {
        "norte": (f"{zone_name}\n~35°C", 0.18, 0.72),
        "centro": ("Centro\n~34°C", 0.50, 0.20),
        "sur": ("Sur\n~28.5°C", 0.78, 0.28),
    }.items():
        if zone in present:
            _add_anno(ax, text, x, y, COLORS[zone])
    _style_map_ax(ax, f"Temperatura superficial (LST) — Verano 2025 — {REGION_TITLES[sub_region]}")
    lst_labels = INC_LST_LABELS if sub_region == "edomex" else LST_LABELS
    ax.legend(handles=_zone_handles(present, custom_labels=lst_labels), fontsize=6.5, loc="lower right", framealpha=0.9)
    _credit(fig, "Fuente: Landsat 8-9, Google Earth Engine")
    _save(fig, f"lst_{REGION_FILES[sub_region]}.png")


def plot_ndvi(mun_gdf, state_bg, sub_region="zmvm"):
    mun, boundary, labels, full = _prepare_mun(mun_gdf, state_bg, sub_region)
    present = set(mun["zone"].unique())

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    _zone_map_base(ax, state_bg, mun, boundary, full_mun_gdf=full)
    _highlight_incidencia(ax, mun)
    if sub_region == "edomex":
        _zoom_edomex(ax)
    zone_name = "Incidencia" if sub_region == "edomex" else "Norte"
    for zone, (text, x, y) in {
        "norte": (f"{zone_name}\nNDVI 0.12", 0.18, 0.72),
        "centro": ("Centro\nNDVI 0.20", 0.50, 0.20),
        "sur": ("Sur\nNDVI 0.33", 0.78, 0.28),
    }.items():
        if zone in present:
            _add_anno(ax, text, x, y, COLORS[zone])
    ax.text(0.05, 0.05,
            "Correlación LST–NDVI: r = –0.829\nA más vegetación, menor temperatura",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=7.5, color="#555555",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8f8f8",
                      edgecolor="#dddddd", linewidth=0.5))
    _style_map_ax(ax, f"Índice de Vegetación (NDVI) — Verano 2025 — {REGION_TITLES[sub_region]}")
    ndvi_labels = INC_NDVI_LABELS if sub_region == "edomex" else NDVI_LABELS
    ax.legend(handles=_zone_handles(present, custom_labels=ndvi_labels), fontsize=6.5, loc="lower right", framealpha=0.9)
    _credit(fig, "Fuente: Landsat 8-9, Google Earth Engine")
    _save(fig, f"ndvi_{REGION_FILES[sub_region]}.png")


def plot_no2(mun_gdf, state_bg, sub_region="zmvm"):
    mun, boundary, labels, full = _prepare_mun(mun_gdf, state_bg, sub_region)
    present = set(mun["zone"].unique())

    st = pd.read_csv(DATA / "processed" / "ground_stations_annual_2023.csv")
    ST_META = {
        "Nezahualcoyotl": "norte", "GAM": "norte",
        "Iztapalapa": "norte", "Ecatepec": "norte",
        "Tlalnepantla": "norte", "Naucalpan": "norte",
        "Centro": "centro", "Benito Juárez": "centro",
        "Hospital General": "centro",
        "Pedregal": "sur", "CCA": "sur",
        "UAM Xochimilco": "sur", "Ajusco Medio": "sur",
    }
    no2 = st[(st["pollutant"] == "NO2") & (st["annual_mean"] > 0)].copy()
    no2["zone"] = no2["station_name"].map(ST_META)
    zone_means = no2.groupby("zone")["annual_mean"].mean()

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    _zone_map_base(ax, state_bg, mun, boundary, full_mun_gdf=full)
    _highlight_incidencia(ax, mun)
    if sub_region == "edomex":
        _zoom_edomex(ax)
    zone_name = "Incidencia" if sub_region == "edomex" else "Norte"
    for zone, label, x, y in [
        ("norte", zone_name, 0.18, 0.72),
        ("centro", "Centro", 0.50, 0.20),
        ("sur", "Sur", 0.78, 0.28),
    ]:
        if zone in present:
            val = zone_means.get(zone, 0)
            _add_anno(ax, f"{label}\n{val:.3f} ppm", x, y, COLORS[zone])
    _style_map_ax(ax, f"Dióxido de Nitrógeno (NO₂) — 2023 — {REGION_TITLES[sub_region]}")
    no2_labels = INC_NO2_LABELS if sub_region == "edomex" else NO2_LABELS
    ax.legend(handles=_zone_handles(present, custom_labels=no2_labels), fontsize=6.5, loc="lower right", framealpha=0.9)
    _credit(fig, "Fuente: SINAICA (estaciones 2023)")
    _save(fig, f"no2_{REGION_FILES[sub_region]}.png")


# ---------------------------------------------------------------------------
# 4. PM₂.₅ — Horizontal bar chart
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 5. Marginación — Municipio choropleth by mean IM_2020
# ---------------------------------------------------------------------------

def plot_marginacion(mun_gdf, state_bg, sub_region="zmvm"):
    mun, boundary, labels, full = _prepare_mun(mun_gdf, state_bg, sub_region)

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    state_bg.plot(ax=ax, color=GRAY_BG, edgecolor="none")

    if sub_region == "edomex":
        # EdoMex no-norte en gris; CDMX + zona norte coloreados
        mun_gdf.plot(ax=ax, color=UNSHADED_FILL, edgecolor=MUN_EC, linewidth=0.6)
        visibles = mun[(mun["CVE_ENT"] == "09") | (mun["zone"] == "norte")].dropna(subset=["IM_2020"])
        if len(visibles) > 0:
            visibles.plot(
                ax=ax, column="IM_2020", cmap="RdYlBu_r",
                linewidth=MUN_LW, edgecolor=MUN_EC,
                legend=True,
                legend_kwds={"label": "IM_2020\npromedio", "shrink": 0.6},
            )
    else:
        has_im = mun.dropna(subset=["IM_2020"]).copy()
        has_im.plot(
            ax=ax, column="IM_2020", cmap="RdYlBu_r",
            linewidth=MUN_LW, edgecolor=MUN_EC,
            legend=True,
            legend_kwds={"label": "IM_2020\npromedio", "shrink": 0.6},
        )

    boundary.plot(ax=ax, color=ZMVM_EC, linewidth=ZMVM_LW)
    _highlight_incidencia(ax, mun)
    _plot_extent(ax, mun)
    if sub_region == "edomex":
        _zoom_edomex(ax)
        inc_patch = Patch(facecolor="#fffbe6", edgecolor=INC_EC, linewidth=2, label="Zona de incidencia")
        ax.legend(handles=[inc_patch], fontsize=7, loc="upper right", framealpha=0.9)
    _style_map_ax(ax, f"Marginación (CONAPO IM_2020)\nPromedio por Municipio — {REGION_TITLES[sub_region]}")
    _credit(fig, "Fuente: CONAPO (Índice de Marginación 2020)")
    _save(fig, f"marginacion_{REGION_FILES[sub_region]}.png")


# ---------------------------------------------------------------------------
# 6. Áreas Verdes — Municipio choropleth
# ---------------------------------------------------------------------------

def plot_areas_verdes(mun_gdf, state_bg, sub_region="zmvm"):
    if sub_region in ("zmvm", "edomex"):
        print(f"  ˟ areas_verdes_{REGION_FILES[sub_region]}.png — skip (datos de áreas verdes solo disponibles para CDMX)")
        return

    mun = _filter_region(mun_gdf, sub_region)
    boundary = _zmvm_boundary(mun)  # CDMX boundary
    gdf_v = mun[mun["area_verde_total_m2"].notna()].copy()
    gdf_v["av_log"] = np.log10(gdf_v["area_verde_total_m2"].clip(lower=1))

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    state_bg.plot(ax=ax, color=GRAY_BG, edgecolor="none")
    gdf_v.plot(
        ax=ax, column="av_log", cmap="YlGn",
        linewidth=MUN_LW, edgecolor=MUN_EC,
        legend=True,
        legend_kwds={
            "shrink": 0.6,
            "label": "Área verde\n(log₁₀ m²)",
        },
    )
    boundary.plot(ax=ax, color=ZMVM_EC, linewidth=ZMVM_LW)
    _highlight_incidencia(ax, mun)
    _plot_extent(ax, mun)
    _style_map_ax(ax, "Áreas Verdes por Alcaldía — CDMX")
    _credit(fig, "Fuente: Inventario SEDEMA 2017 — árboles, parques, áreas protegidas y conservación")
    _save(fig, f"areas_verdes_{REGION_FILES[sub_region]}.png")


# ---------------------------------------------------------------------------
# Bar/column charts (kept from original version for data comparison)
# ---------------------------------------------------------------------------

CHART_COLORS = {"norte": "#E63946", "centro": "#F4A261", "sur": "#2A9D8F"}
CHART_LABELS = {"norte": "Norte", "centro": "Centro", "sur": "Sur"}
CHART_FIG_SIZE = (7.2, 7.2)
CHART_CREDIT = "Fuente: Landsat 8-9 / Sentinel-5P / SINAICA / CONAPO"


def _chart_legend():
    return [
        Patch(facecolor=CHART_COLORS["norte"], label="Norte (nororiente)"),
        Patch(facecolor=CHART_COLORS["centro"], label="Centro"),
        Patch(facecolor=CHART_COLORS["sur"], label="Sur (referencia)"),
    ]


def _chart_style(ax, title, ylabel=""):
    ax.set_title(title, fontsize=13, fontweight="bold", color=TITLE_COLOR, pad=12)
    ax.set_ylabel(ylabel, fontsize=9, color="#444444")
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_lst_chart():
    zones = ["Norte\n(nororiente)", "Centro", "Sur\n(referencia)"]
    values = [37.5, 34.0, 28.5]
    colors = [CHART_COLORS["norte"], CHART_COLORS["centro"], CHART_COLORS["sur"]]
    err = [2.5, 2.0, 2.0]

    fig, ax = plt.subplots(figsize=CHART_FIG_SIZE)
    bars = ax.bar(zones, values, color=colors, width=0.55,
                  yerr=err, capsize=6, edgecolor="white", linewidth=1.2)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2,
                f"{v:.0f}°C", ha="center", fontsize=11, fontweight="bold", color=TITLE_COLOR)
    _chart_style(ax, "Temperatura superficial (LST)\nVerano 2025", "°C")
    ax.set_ylim(0, 48)
    fig.text(0.5, 0.01, "Fuente: Landsat 8-9, Google Earth Engine", ha="center", va="bottom", fontsize=7, color="#666666")
    _save(fig, "lst_chart_zmvm.png")


def plot_ndvi_chart():
    zones = ["Norte\n(nororiente)", "Centro", "Sur\n(referencia)"]
    values = [0.12, 0.20, 0.33]
    colors = [CHART_COLORS["norte"], CHART_COLORS["centro"], CHART_COLORS["sur"]]

    fig, ax = plt.subplots(figsize=CHART_FIG_SIZE)
    bars = ax.bar(zones, values, color=colors, width=0.55, edgecolor="white", linewidth=1.2)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f"{v:.2f}", ha="center", fontsize=11, fontweight="bold", color=TITLE_COLOR)
    _chart_style(ax, "Índice de Vegetación (NDVI)\nVerano 2025", "NDVI")
    ax.set_ylim(0, 0.42)
    ax.text(0.95, 0.05,
            "Correlación LST–NDVI: r = –0.829\nA más vegetación, menor temperatura",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7.5, color="#555555",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8f8f8",
                      edgecolor="#dddddd", linewidth=0.5))
    fig.text(0.5, 0.01, "Fuente: Landsat 8-9, Google Earth Engine", ha="center", va="bottom", fontsize=7, color="#666666")
    _save(fig, "ndvi_chart_zmvm.png")


def plot_no2_chart():
    st = pd.read_csv(DATA / "processed" / "ground_stations_annual_2023.csv")
    ST_META = {
        "Nezahualcoyotl": "norte", "GAM": "norte", "Iztapalapa": "norte",
        "Ecatepec": "norte", "Tlalnepantla": "norte", "Naucalpan": "norte",
        "Centro": "centro", "Benito Juárez": "centro", "Hospital General": "centro",
        "Pedregal": "sur", "CCA": "sur", "UAM Xochimilco": "sur", "Ajusco Medio": "sur",
    }
    no2 = st[(st["pollutant"] == "NO2") & (st["annual_mean"] > 0)].copy()
    no2["zone"] = no2["station_name"].map(ST_META)
    no2 = no2.sort_values("annual_mean")

    fig, ax = plt.subplots(figsize=CHART_FIG_SIZE)
    names = no2["station_name"].tolist()
    vals = no2["annual_mean"].tolist()
    colors_bar = [CHART_COLORS[z] for z in no2["zone"]]
    ax.barh(names, vals, color=colors_bar, height=0.65, edgecolor="white", linewidth=0.8)
    for bar, v in zip(ax.containers[0], vals):
        ax.text(bar.get_width() + 0.0003, bar.get_y() + bar.get_height() / 2,
                f"{v:.3f}", va="center", fontsize=7.5, color="#444444")
    _chart_style(ax, "Dióxido de Nitrógeno (NO₂)\nEstaciones SINAICA 2023", "ppm")
    ax.set_xlabel("NO₂ (ppm)", fontsize=9, color="#444444")
    ax.legend(handles=_chart_legend(), fontsize=8, loc="lower right")
    fig.text(0.5, 0.01, "Fuente: SINAICA (estaciones 2023)", ha="center", va="bottom", fontsize=7, color="#666666")
    _save(fig, "no2_chart_zmvm.png")


# ---------------------------------------------------------------------------
# 7. PM₂.₅ / PM₁₀ — Bar charts + Kriging interpolated surfaces
# ---------------------------------------------------------------------------

def plot_pm_chart():
    st = pd.read_csv(DATA / "processed" / "ground_stations_annual_2023.csv")
    ST_META = {
        "Nezahualcoyotl": "norte", "GAM": "norte", "Iztapalapa": "norte",
        "Ecatepec": "norte", "Tlalnepantla": "norte", "Naucalpan": "norte",
        "Centro": "centro", "Benito Juárez": "centro", "Hospital General": "centro",
        "Pedregal": "sur", "CCA": "sur", "UAM Xochimilco": "sur", "Ajusco Medio": "sur",
    }
    pm = st[(st["pollutant"] == "PM2.5") & (st["annual_mean"] > 0)].copy()
    pm["zone"] = pm["station_name"].map(ST_META)
    pm = pm.sort_values("annual_mean")

    fig, ax = plt.subplots(figsize=CHART_FIG_SIZE)
    names = pm["station_name"].tolist()
    vals = pm["annual_mean"].tolist()
    colors_bar = [CHART_COLORS[z] for z in pm["zone"]]
    ax.barh(names, vals, color=colors_bar, height=0.65, edgecolor="white", linewidth=0.8)
    for bar, v in zip(ax.containers[0], vals):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{v:.1f}", va="center", fontsize=7.5, color="#444444")
    ax.axvline(5, color="#c0392b", linestyle="--", linewidth=2, alpha=0.7)
    ax.text(5.2, -0.6, "WHO (5 µg/m³)", fontsize=7.5, color="#c0392b")
    _chart_style(ax, "Partículas finas (PM₂.₅)\nEstaciones SINAICA 2023", "µg/m³")
    ax.set_xlabel("µg/m³", fontsize=9, color="#444444")
    ax.set_xlim(0, max(vals) * 1.25)
    ax.legend(handles=_chart_legend(), fontsize=8, loc="lower right")
    fig.text(0.5, 0.01, "Fuente: SINAICA / RAMA (estaciones 2023)", ha="center", va="bottom", fontsize=7, color="#666666")
    _save(fig, "pm_chart_zmvm.png")


def plot_pm10_chart():
    st = pd.read_csv(DATA / "processed" / "ground_stations_annual_2023.csv")
    ST_META = {
        "Nezahualcoyotl": "norte", "GAM": "norte", "Iztapalapa": "norte",
        "Ecatepec": "norte", "Tlalnepantla": "norte", "Naucalpan": "norte",
        "Centro": "centro", "Benito Juárez": "centro", "Hospital General": "centro",
        "Pedregal": "sur", "CCA": "sur", "UAM Xochimilco": "sur", "Ajusco Medio": "sur",
    }
    pm = st[(st["pollutant"] == "PM10") & (st["annual_mean"] > 0)].copy()
    pm["zone"] = pm["station_name"].map(ST_META)
    pm = pm.sort_values("annual_mean")

    fig, ax = plt.subplots(figsize=CHART_FIG_SIZE)
    names = pm["station_name"].tolist()
    vals = pm["annual_mean"].tolist()
    colors_bar = [CHART_COLORS[z] for z in pm["zone"]]
    ax.barh(names, vals, color=colors_bar, height=0.65, edgecolor="white", linewidth=0.8)
    for bar, v in zip(ax.containers[0], vals):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{v:.1f}", va="center", fontsize=7.5, color="#444444")
    ax.axvline(15, color="#c0392b", linestyle="--", linewidth=2, alpha=0.7)
    ax.text(15.2, -0.6, "WHO (15 µg/m³)", fontsize=7.5, color="#c0392b")
    _chart_style(ax, "Partículas (PM₁₀)\nEstaciones SINAICA 2023", "µg/m³")
    ax.set_xlabel("µg/m³", fontsize=9, color="#444444")
    ax.set_xlim(0, max(vals) * 1.25)
    ax.legend(handles=_chart_legend(), fontsize=8, loc="lower right")
    fig.text(0.5, 0.01, "Fuente: SINAICA / RAMA (estaciones 2023)", ha="center", va="bottom", fontsize=7, color="#666666")
    _save(fig, "pm10_chart_zmvm.png")


def _surface_map(mun_gdf, state_bg, pollutant):
    from src.stations import STATIONS_META
    from src.interpolation import prepare_station_data, kriging_surface

    # Metadata per pollutant
    meta = {
        "PM2.5": {"who": 5, "unit": "µg/m³", "label": "PM₂.₅", "file": "pm_zmvm.png"},
        "PM10":  {"who": 15, "unit": "µg/m³", "label": "PM₁₀", "file": "pm10_zmvm.png"},
        "NO2":   {"who": 0.021, "unit": "ppm", "label": "NO₂",  "file": "no2_zmvm.png"},
    }
    m = meta.get(pollutant)
    if m is None:
        print(f"  ˟ pollutant '{pollutant}' not supported for surface maps")
        return
    who_limit, unit, label, save_name = m["who"], m["unit"], m["label"], m["file"]

    st = pd.read_csv(DATA / "processed" / "ground_stations_annual_2023.csv")
    station_df = prepare_station_data(st, pollutant, STATIONS_META)

    if len(station_df) < 4:
        print(f"  ˟ {save_name} — skip (solo {len(station_df)} estaciones con datos)")
        return

    # Pad must be large enough so the grid covers the entire CDMX+incidencia polygon,
    # not just the station bounding box.  Stations (central-north) are ~0.24° north
    # of the polygon's southern tip (Milpa Alta), so pad=0.25 covers it.
    surface = kriging_surface(station_df, resolution=0.005, pad=0.25,
                              variogram_model="spherical")

    # CDMX + incidencia-norte polygon for masking the raster
    # (stations are only in CDMX + the northern EdoMex corridor)
    cdmx_inc = mun_gdf[
        (mun_gdf["CVE_ENT"] == "09") |
        ((mun_gdf["CVE_ENT"] == "15") & (mun_gdf["zone"] == "norte"))
    ].copy()
    clip_poly = cdmx_inc.dissolve().iloc[0].geometry
    if clip_poly.geom_type == "MultiPolygon":
        clip_poly = clip_poly.convex_hull

    # Value range for consistent colormap
    vmin = station_df["value"].min() * 0.9
    vmax = station_df["value"].max() * 1.1

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    # Background: CDMX + incidencia polygon (not full EdoMex)
    bg_gdf = gpd.GeoSeries([clip_poly], crs="EPSG:4326")
    bg_gdf.plot(ax=ax, color=GRAY_BG, edgecolor="none")

    # Mask grid outside CDMX+incidencia polygon
    from shapely.geometry import Point
    mask = np.zeros(surface["z"].shape, dtype=bool)
    for i in range(surface["z"].shape[0]):
        for j in range(surface["z"].shape[1]):
            if not clip_poly.contains(Point(surface["lng"][i, j],
                                            surface["lat"][i, j])):
                mask[i, j] = True
    z_masked = np.ma.masked_where(mask, surface["z"])

    # Interpolated surface clipped
    surf = ax.pcolormesh(
        surface["lng"], surface["lat"], z_masked,
        cmap="RdYlBu_r", vmin=vmin, vmax=vmax, alpha=0.85,
        shading="auto", zorder=2,
    )

    # Municipio boundaries of CDMX + incidencia only
    cdmx_inc.plot(ax=ax, facecolor="none", edgecolor=MUN_EC, linewidth=0.4,
                  zorder=3)

    # CDMX + incidencia outer boundary
    bg_gdf.boundary.plot(ax=ax, color=ZMVM_EC, linewidth=ZMVM_LW, zorder=4)

    # Highlight incidencia zone
    _highlight_incidencia(ax, mun_gdf)

    # Station points: color by value, labelled
    sc = ax.scatter(
        station_df["lng"], station_df["lat"],
        c=station_df["value"], cmap="RdYlBu_r",
        vmin=vmin, vmax=vmax,
        edgecolor="#333333", linewidth=1.5, s=80, zorder=6,
    )
    for _, row in station_df.iterrows():
        val = row["value"]
        fmt = ".3f" if pollutant == "NO2" else ".1f"
        ax.annotate(
            f"{val:{fmt}}", (row["lng"], row["lat"]),
            fontsize=6.5, fontweight="bold", color="#1a1a2e",
            ha="center", va="bottom",
            textcoords="offset points", xytext=(0, 10),
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.85),
        )

    # Extent focused on CDMX + incidencia
    bounds = clip_poly.bounds
    dx = (bounds[2] - bounds[0]) * PAD
    dy = (bounds[3] - bounds[1]) * PAD
    ax.set_xlim(bounds[0] - dx, bounds[2] + dx)
    ax.set_ylim(bounds[1] - dy, bounds[3] + dy)

    # Colorbar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.015)
    cbar.set_label(f"{label} ({unit})", fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    # WHO guideline reference annotation
    ax.text(
        0.97, -0.02,
        f"Línea base OMS\n{label}: {who_limit} {unit}/año",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=8, color="#c0392b",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                  edgecolor="#c0392b", linewidth=1.5),
    )

    _style_map_ax(ax, f"{label} — Interpolación Kriging\nEstaciones SINAICA 2023")
    source = "SINAICA" if pollutant == "NO2" else "SINAICA / RAMA"
    _credit(fig, f"Fuente: {source} (estaciones 2023)")
    _save(fig, save_name)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("Loading state boundaries...")
    state_bg = _load_state_bg()
    print(f"  {len(state_bg)} states loaded")

    print("\nLoading and dissolving AGEBs to municipios...")
    mun_gdf = _load_municipios()
    print(f"  {len(mun_gdf)} ZMVM municipio/alcaldía polygons")

    print("\n--- Geographic maps (municipio-level) ---")
    GEO_FUNCS = [
        (plot_lst, "lst"),
        (plot_ndvi, "ndvi"),
        (plot_no2, "no2"),
        (plot_marginacion, "marginacion"),
        (plot_areas_verdes, "areas_verdes"),
    ]
    for fn, base in GEO_FUNCS:
        for sub in ["zmvm", "cdmx", "edomex"]:
            if base in ("lst", "ndvi", "no2") and sub == "zmvm":
                print(f"  ˟ {base}_zmvm.png — skip (no per-municipio data)")
                continue
            name = f"{base}_{REGION_FILES[sub]}.png"
            print(f"  Generating {name}...")
            fn(mun_gdf, state_bg, sub_region=sub)

    print("\n--- Charts (bar/column for data comparison) ---")
    for fn, name in [
        (plot_lst_chart, "lst_chart_zmvm.png"),
        (plot_ndvi_chart, "ndvi_chart_zmvm.png"),
        (plot_no2_chart, "no2_chart_zmvm.png"),
    ]:
        print(f"  Generating {name}...")
        fn()

    print("\n--- PM bar charts ---")
    for fn, name in [
        (plot_pm_chart, "pm_chart_zmvm.png"),
        (plot_pm10_chart, "pm10_chart_zmvm.png"),
    ]:
        print(f"  Generating {name}...")
        fn()

    print("\n--- PM interpolated surface maps (CDMX + incidencia) ---")
    for p_name in ["PM2.5", "PM10"]:
        print(f"  Generating pm{'10' if p_name == 'PM10' else ''}_zmvm.png...")
        _surface_map(mun_gdf, state_bg, p_name)

    print("\n--- NO₂ interpolated surface map (CDMX + incidencia) ---")
    print("  Generating no2_zmvm.png...")
    _surface_map(mun_gdf, state_bg, "NO2")

    print("\n✓ Done — all maps and charts exported.")
