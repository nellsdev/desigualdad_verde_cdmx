"""
Dashboard: Dos Méxicos Under the Same Sun
Green Inequality, Urban Heat Islands, and Air Quality in Mexico City

Run with: streamlit run dashboards/app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dos Méxicos Bajo el Mismo Sol",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
MAPAS = ROOT / "outputs" / "mapas" / "zmvm"

# ---------------------------------------------------------------------------
# Zone colours
# ---------------------------------------------------------------------------
COLORS = {
    "norte": "#E74C3C",
    "centro": "#F39C12",
    "sur": "#27AE60",
}

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #A0A0A0;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #333;
    }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #A0A0A0;
    }
    .key-finding {
        background-color: #1A1A2E;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #E74C3C;
        margin: 1rem 0;
    }
    .zone-norte { color: #E74C3C; font-weight: 600; }
    .zone-centro { color: #F39C12; font-weight: 600; }
    .zone-sur { color: #27AE60; font-weight: 600; }
    .citation {
        font-size: 0.8rem;
        color: #666;
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #333;
    }
    @media (max-width: 768px) {
        .hero-title { font-size: 1.8rem; }
    }
</style>
""", unsafe_allow_html=True)

# ===========================================================================
# HERO
# ===========================================================================
st.markdown(
    f'<div class="hero-title">☀️ Dos Méxicos<br>Bajo el Mismo Sol</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-sub">'
    "Green Inequality, Urban Heat Islands, and Air Quality in Mexico City"
    "</div>",
    unsafe_allow_html=True,
)

# Quick stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="stat-number">5–10 °C</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Norte-sur gap en temperatura</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stat-number">~2000</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Productos analizados</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="stat-number">20</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Municipios en zona de estudio</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="stat-number">6</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Indicadores integrados</div>', unsafe_allow_html=True)

st.divider()

# ===========================================================================
# SECTION 1 — THE PROBLEM
# ===========================================================================
st.markdown('<div class="section-header">🔬 El Problema</div>', unsafe_allow_html=True)

left, right = st.columns([1.2, 1])

with left:
    st.markdown(
        """
        La Zona Metropolitana del Valle de México (ZMVM) es una de las áreas urbanas más grandes del
        mundo — 22 millones de personas en 76 municipios. Pero la ciudad no es uniforme.
        
        Algunas colonias tienen calles arboladas, parques y aire fresco. Otras tienen concreto,
        asfalto y humo de escape.
        
        **¿La brecha ambiental en la CDMX se puede medir desde el espacio?**
        
        Este proyecto responde esa pregunta con datos satelitales de la NASA (Landsat 8/9) y la
        ESA (Sentinel-5P), combinados con datos censales de INEGI, monitoreo de calidad del
        aire (SINAICA) y registros de salud pública (DGIS).
        """
    )

with right:
    st.image(
        str(MAPAS / "no2_zmvm.png"),
        caption="NO₂ troposférico en la ZMVM — Sentinel-5P TROPOMI (ESA). Las zonas rojas son las más contaminadas.",
        width="stretch",
    )

st.divider()

# ===========================================================================
# SECTION 2 — TEMPERATURE & VEGETATION
# ===========================================================================
st.markdown('<div class="section-header">🌡️ Temperatura y Vegetación</div>', unsafe_allow_html=True)

st.markdown(
    """
    El norte de la ZMVM es **5–10 °C más caliente** que el sur, tanto en verano como en invierno.
    No es un fenómeno meteorológico puntual — es estructural.
    """
)

col_lst, col_ndvi = st.columns(2)

with col_lst:
    st.image(
        str(MAPAS / "lst_chart_zmvm.png"),
        caption="Temperatura superficial (Landsat 8/9). El norte promedia ~35 °C, el sur ~27 °C.",
        width="stretch",
    )

with col_ndvi:
    st.image(
        str(MAPAS / "ndvi_chart_zmvm.png"),
        caption="Índice de vegetación NDVI. El norte tiene menos de la mitad de vegetación que el sur.",
        width="stretch",
    )

st.markdown(
    """
    <div class="key-finding">
        <strong>Correlación LST–NDVI: r = −0.936 a nivel municipio (n = 21)</strong><br>
        En el cinturón de concreto, medido por muestreo de 400 píxeles en el notebook 02,
        la correlación reportada es r = −0.829 — pendiente de reproducir (ver Limitaciones).
        Donde no hay árboles, el calor se queda.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ===========================================================================
# SECTION 3 — AIR POLLUTION
# ===========================================================================
st.markdown('<div class="section-header">💨 Contaminación Atmosférica</div>', unsafe_allow_html=True)

st.markdown(
    """
    La misma geografía que es más caliente y tiene menos vegetación también respira aire más contaminado.
    Combinamos datos satelitales (NO₂ troposférico) con datos de 13 estaciones de monitoreo en tierra.
    """
)

col_no2, col_pm = st.columns(2)

with col_no2:
    st.image(
        str(MAPAS / "no2_chart_zmvm.png"),
        caption="NO₂ satelital (Sentinel-5P). El norte tiene 30–50% más NO₂ que el sur.",
        width="stretch",
    )

with col_pm:
    st.image(
        str(MAPAS / "pm_chart_zmvm.png"),
        caption="Material particulado (PM₂.₅ y PM₁₀) en estaciones SINAICA.",
        width="stretch",
    )

st.markdown(
    """
    <div class="key-finding">
        <strong>TODAS las estaciones de monitoreo EXCEDEN los límites anuales de la OMS</strong><br>
        • PM₂.₅: norte 27.5 µg/m³, sur 14.4 µg/m³ — límite OMS: 5 µg/m³<br>
        • PM₁₀: norte 54.3 µg/m³, sur 32.8 µg/m³ — límite OMS: 15 µg/m³
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ===========================================================================
# SECTION 4 — SOCIAL DIMENSION + HEALTH
# ===========================================================================
st.markdown('<div class="section-header">🧭 Dimensión Social y Salud</div>', unsafe_allow_html=True)

st.markdown(
    """
    La marginación socioeconómica no está distribuida uniformemente — y se correlaciona casi
    perfectamente con la división ambiental.
    """
)

left, right = st.columns(2)

with left:
    st.image(
        str(MAPAS / "marginacion_zmvm.png"),
        caption="Índice de Marginación (CONAPO) por municipio. Las zonas más calientes son las más marginadas.",
        width="stretch",
    )

with right:
    st.markdown(
        """
        ### Hallazgos clave
        
        - **IM_2020 y LST: r = +0.30, no significativo con n = 21 municipios.** La dirección
          acompaña la hipótesis, pero la muestra municipal no alcanza para sostenerla.
        
        - **La gradiente marginación–salud respiratoria NO es monotónica.** Las medianas por
          grado de marginación son 17,266 (Muy bajo), 14,153 (Bajo), 16,066 (Medio) y 21,961
          (Alto) por 100 mil habitantes. Solo el grado "Alto" se despega del resto.
        
        - **El área verde no muestra un efecto protector con esta métrica.** La correlación con
          la tasa respiratoria es *positiva* (r = +0.52) porque la métrica suma todo el
          inventario de áreas verdes, camellones e instalaciones incluidos.
        
        - **Correlación marginación–tasa respiratoria: r = −0.06 a nivel AGEB (n = 3,419).**
          Prácticamente nula. La desigualdad ambiental está bien medida; su vínculo con la
          salud respiratoria, no.
        """
    )

st.divider()

# ===========================================================================
# SECTION 5 — INTEGRATED BURDEN HEATMAP
# ===========================================================================
st.markdown('<div class="section-header">🔥 Carga Integrada — El Mapa Completo</div>', unsafe_allow_html=True)

st.markdown(
    """
    Combinamos los 6 indicadores (LST, NDVI, NO₂, PM₂.₅, marginación, salud respiratoria)
    en un ranking integrado por municipio. El resultado muestra quién carga con el peso
    más pesado de la desigualdad ambiental.
    """
)

# --- INTEGRATED BURDEN TABLE ---
# Read from the aggregated table that notebook 07 exports, so the numbers shown
# here are exactly the ones quoted in the README.
#
# An earlier version of this section carried hardcoded placeholder values with a
# comment claiming they came "from the README findings". They did not: they listed
# 10 municipios instead of 21, the respiratory rates were off by 2-3x, and the zone
# assignment was the old README one rather than the one in the data.
_burden = pd.read_csv(
    ROOT / "dashboards" / "data" / "municipio_completo.csv"
).sort_values("burden_score", ascending=True)

df_burden = pd.DataFrame({
    "Municipio": _burden["NOM_MUN"],
    "Zona": _burden["zona"],
    "LST °C": _burden["lst_mean"],
    "NDVI": _burden["ndvi_mean"],
    "NO₂ (×10⁻⁵)": _burden["no2_mean"] * 1e5,
    "PM₂.₅ µg/m³": _burden["pm25_mean"],
    "IMN": _burden["imn_mean"],
    "Tasa Resp.": _burden["tasa_respiratoria"],
    "Carga (menor = peor)": _burden["burden_score"],
}).reset_index(drop=True)

# Color-coded zone column
def zone_color(val: str) -> str:
    colors = {"Norte": "#E74C3C", "Centro": "#F39C12", "Sur": "#27AE60"}
    return f"background-color: {colors.get(val, '#888')}; color: white; font-weight: 600;"

# Styler.map replaced Styler.applymap in pandas 2.1, and applymap was removed in
# pandas 3.0 -- which is the version Streamlit Community Cloud installs. The
# fallback keeps the app working on either.
_burden_style = df_burden.style
_zone_styler = getattr(_burden_style, "map", None) or _burden_style.applymap

styled = (
    _zone_styler(zone_color, subset=["Zona"])
    .format({
        "LST °C": "{:.1f}",
        "NDVI": "{:.2f}",
        "NO₂ (×10⁻⁵)": "{:.1f}",
        "PM₂.₅ µg/m³": "{:.1f}",
        "IMN": "{:.3f}",
        "Tasa Resp.": "{:,.0f}",
        "Carga (menor = peor)": "{:.2f}",
    })
)

st.dataframe(styled, width="stretch", hide_index=True)

st.markdown(
    """
    <div class="key-finding">
        <strong>Cuauhtémoc, Azcapotzalco y Benito Juárez encabezan la carga integrada;</strong>
        Gustavo A. Madero queda 4º. El ranking está dominado por el
        <span class="zone-centro">centro</span>, empujado por el NO₂ del tráfico, y no solo por
        la periferia <span class="zone-norte">norte</span>.<br><br>
        La narrativa norte–sur es sólida para temperatura y vegetación, pero se rompe al agregar
        contaminación: el centro también carga de forma severa. Las alcaldías del
        <span class="zone-sur">sur</span> siguen siendo las mejor posicionadas. La columna
        "Carga" ordena la tabla: menor valor = mayor carga combinada.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ===========================================================================
# SECTION 6 — SURVEY (preliminary)
# ===========================================================================
st.markdown('<div class="section-header">📋 Encuesta Ciudadana — Avance</div>', unsafe_allow_html=True)

st.markdown(
    """
    Los satélites nos dan datos, pero lo que no registran es cómo se vive esta desigualdad
    en el día a día. Por eso lanzamos una encuesta ciudadana anónima sobre percepción
    ambiental y salud en la ZMVM.
    """
)

col_survey1, col_survey2, col_survey3 = st.columns(3)
with col_survey1:
    st.markdown('<div class="stat-number">33</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Respuestas hasta ahora</div>', unsafe_allow_html=True)
with col_survey2:
    st.markdown('<div class="stat-number">18</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Preguntas</div>', unsafe_allow_html=True)
with col_survey3:
    st.markdown('<div class="stat-number">~5 min</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-label">Tiempo estimado</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="background-color: #1A1A2E; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
        <strong>🏁 Meta: 100 respuestas</strong><br>
        Necesitamos más voces del norte de la ciudad (Ecatepec, GAM, Neza, Tlalnepantla, Naucalpan, Iztapalapa)
        para equilibrar la muestra. Los resultados se publicarán abiertamente para fortalecer
        la exigencia de justicia ambiental en la ZMVM.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ===========================================================================
# FOOTER
# ===========================================================================
st.markdown(
    '<div class="section-header">📖 Sobre el Proyecto</div>',
    unsafe_allow_html=True,
)

col_about1, col_about2 = st.columns(2)

with col_about1:
    st.markdown(
        """
        **Datos y métodos**
        
        - **Temperatura superficial:** Landsat 8/9 (NASA), bandas térmicas, verano 2023
        - **Vegetación:** NDVI desde Landsat 8/9
        - **NO₂ troposférico:** Sentinel-5P TROPOMI (ESA), anual 2023
        - **Material particulado:** 13 estaciones SINAICA (INECC), promedio anual
        - **Marginación:** CONAPO, Índice de Marginación 2020 por AGEB
        - **Salud:** DGIS, egresos hospitalarios por enfermedades respiratorias (J00–J99)
        """
    )

with col_about2:
    st.markdown(
        """
        **Stack tecnológico**
        
        | Herramienta | Uso |
        |---|---|
        | Python 3.10+ | Lenguaje principal |
        | Google Earth Engine | Procesamiento satelital |
        | geopandas / shapely | Análisis espacial vectorial |
        | matplotlib | Visualización estática |
        | Streamlit | Dashboard interactivo |
        
        ---
        
        **Autora:** Nelly Itzel Rodríguez Ortiz  
        Ingeniera en Computación, MSc. Microelectrónica  
        Procesamiento de señales e información aplicado a datos ambientales
        """
    )

st.markdown(
    '<div class="citation">'
    "Proyecto de código abierto — "
    '<a href="https://github.com/nellsdev">github.com/nellsdev</a>'
    "</div>",
    unsafe_allow_html=True,
)
