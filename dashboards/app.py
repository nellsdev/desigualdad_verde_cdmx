"""
Dashboard: Dos Méxicos Bajo el Mismo Sol
Desigualdad ambiental en la Ciudad de México.

Run with: streamlit run dashboards/app.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dos Méxicos bajo el mismo sol",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
MAPAS = ROOT / "outputs" / "mapas" / "zmvm"
GRAFICOS = ROOT / "outputs" / "graficos"
DATA = ROOT / "dashboards" / "data"

# ---------------------------------------------------------------------------
# Zone colours (kept in sync with scripts/export_maps.py)
# ---------------------------------------------------------------------------
COLORS = {"Norte": "#C0392B", "Centro": "#B9770E", "Sur": "#1E8449"}

# ---------------------------------------------------------------------------
# Style
#
# Colours are expressed with opacity and rgba() instead of fixed greys so the
# page reads correctly on a light or a dark background. The base theme is set in
# .streamlit/config.toml, and the type scale is deliberately narrow: the hero is
# 2.1rem against 1rem body text, not 2.6rem against 1rem.
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
    .hero-title {
        font-size: 2.1rem; font-weight: 800; letter-spacing: -0.02em;
        line-height: 1.15; margin-bottom: 0.4rem;
    }
    .hero-sub {
        font-size: 1.02rem; opacity: 0.75; margin-bottom: 1.4rem;
    }
    .hook {
        font-size: 1.22rem; line-height: 1.55; font-weight: 500;
        margin: 0.4rem 0 1.4rem 0;
    }
    .section-header {
        font-size: 1.45rem; font-weight: 700; margin-top: 2.2rem;
        margin-bottom: 0.9rem; padding-bottom: 0.45rem;
        border-bottom: 1px solid rgba(128, 128, 128, 0.35);
    }
    .stat-number { font-size: 1.8rem; font-weight: 800; line-height: 1.05; }
    .stat-label  { font-size: 0.9rem; opacity: 0.7; }
    .card {
        padding: 1.05rem 1.2rem; border-radius: 8px; margin: 1rem 0;
        border-left: 4px solid #C0392B;
        background: rgba(128, 128, 128, 0.09);
    }
    .card.good { border-left-color: #1E8449; }
    .card.null { border-left-color: #7F8C8D; }
    .zone-norte  { color: #C0392B; font-weight: 600; }
    .zone-centro { color: #B9770E; font-weight: 600; }
    .zone-sur    { color: #1E8449; font-weight: 600; }
    .citation {
        font-size: 0.85rem; opacity: 0.6; text-align: center;
        margin-top: 3rem; padding-top: 1.5rem;
        border-top: 1px solid rgba(128, 128, 128, 0.3);
    }
    @media (max-width: 768px) {
        .hero-title { font-size: 1.6rem; }
        .hook { font-size: 1.08rem; }
        .section-header { font-size: 1.22rem; }
        .stat-number { font-size: 1.45rem; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ===========================================================================
# HERO
# ===========================================================================
st.markdown('<div class="hero-title">Dos Méxicos bajo el mismo sol</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Desigualdad ambiental en la Zona Metropolitana del Valle de '
    "México, medida con datos satelitales, monitoreo de aire, censo y registros de salud."
    "</div>",
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hook">En la misma ciudad, unos viven a 40 °C y otros a 22 °C. '
    "Eso no lo decide el clima: lo decide cuánto concreto y cuánta vegetación tiene "
    "tu colonia.</div>",
    unsafe_allow_html=True,
)

_c1, _c2, _c3, _c4 = st.columns(4)
for col, number, label in [
    (_c1, "9.2 °C", "de brecha de temperatura entre el norte y el sur"),
    (_c2, "+66 %", "más vegetación (NDVI) en el sur que en el norte"),
    (_c3, "21", "municipios y 3,419 AGEBs analizados"),
    (_c4, "34", "respuestas ciudadanas — la encuesta sigue abierta"),
]:
    with col:
        st.markdown(f'<div class="stat-number">{number}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-label">{label}</div>', unsafe_allow_html=True)

st.divider()

# ===========================================================================
# 1 — EL CONTRASTE
# ===========================================================================
st.markdown('<div class="section-header">1. El contraste</div>', unsafe_allow_html=True)

left, right = st.columns([1.15, 1])

with left:
    st.markdown(
        """
        La ZMVM alberga a unas 22 millones de personas en 76 municipios. Pero no es una sola
        ciudad: es una donde el ambiente cambia según dónde te tocó vivir.

        Medimos la temperatura de la superficie con imágenes térmicas de los satélites Landsat
        8 y 9. La diferencia entre la zona norte y la zona sur es de **9.2 °C en promedio**, y
        de **17.7 °C entre el municipio más caliente y el más frío**.

        La vegetación sigue el mismo patrón: el sur tiene **66 % más** índice verde que el norte.

        **Este contraste ambiental es el hallazgo más sólido del proyecto**, y se sostiene con
        cinco mediciones independientes que no dependen una de otra.
        """
    )

with right:
    st.image(
        str(MAPAS / "marginacion_zmvm.png"),
        caption="Índice de Marginación (CONAPO 2020) por municipio. La marginación media es casi "
        "idéntica en las tres zonas (0.950 / 0.958 / 0.953) — ver sección 4.",
        width="stretch",
    )

st.divider()

# ===========================================================================
# 2 — TEMPERATURA Y VEGETACIÓN
# ===========================================================================
st.markdown('<div class="section-header">2. Temperatura y vegetación</div>', unsafe_allow_html=True)

st.markdown(
    """
    La brecha térmica aparece tanto en verano como en invierno, así que no es un fenómeno
    meteorológico puntual: es estructural, y está determinada por el tipo de superficie.
    """
)

st.image(
    str(MAPAS / "lst_chart_zmvm.png"),
    caption="Temperatura superficial media por zona (Landsat 8/9). Norte 35.9 °C, "
    "Centro 36.1 °C, Sur 26.7 °C.",
    width="stretch",
)

st.image(
    str(MAPAS / "ndvi_chart_zmvm.png"),
    caption="Índice de vegetación NDVI por zona. Norte 0.144, Centro 0.115, Sur 0.239.",
    width="stretch",
)

st.markdown(
    """
    <div class="card good">
        <strong>LST–NDVI: r = −0.936 a nivel municipio (n = 21)</strong><br>
        Donde no hay árboles, el calor se queda. En el cinturón de concreto, el muestreo de
        400 píxeles del notebook 02 da r = −0.829 — ese valor todavía no es reproducible desde
        los archivos publicados, y así está declarado.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ===========================================================================
# 3 — CONTAMINACIÓN
# ===========================================================================
st.markdown('<div class="section-header">3. Contaminación atmosférica</div>', unsafe_allow_html=True)

st.markdown(
    """
    La contaminación no sigue una línea norte–sur simple. El **NO₂ más alto está en el centro**
    (22.4 ×10⁻⁵ mol/m²), no en el norte (18.3), porque el centro concentra el tráfico. Ese
    detalle importa: rompe la lectura fácil de "periferia mala, centro bueno".
    """
)

st.image(
    str(MAPAS / "no2_chart_zmvm.png"),
    caption="NO₂ troposférico por zona (Sentinel-5P TROPOMI). Centro 22.4, Norte 18.3, Sur 13.1.",
    width="stretch",
)

st.image(
    str(MAPAS / "pm_chart_zmvm.png"),
    caption="PM₂.₅ en las estaciones SINAICA que reportan datos. Todas superan el límite "
    "anual de la OMS de 5 µg/m³. Varias estaciones del registro original reportan 0.000 en "
    "más de la mitad del año: ver la sección 6.",
    width="stretch",
)

st.image(
    str(MAPAS / "no2_zmvm.png"),
    caption="Distribución espacial del NO₂ troposférico en la ZMVM (Sentinel-5P).",
    width="stretch",
)

st.markdown(
    """
    <div class="card good">
        <strong>Las estaciones de monitoreo superan los límites anuales de la OMS</strong><br>
        Ninguna zona de la ciudad respira aire dentro de la guía anual de PM₂.₅ (5 µg/m³). La
        diferencia entre zonas existe, pero es mucho menor que la brecha de temperatura.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ===========================================================================
# 4 — LO QUE NO SE SOSTIENE
# ===========================================================================
st.markdown('<div class="section-header">4. Lo que no se sostiene</div>', unsafe_allow_html=True)

st.markdown(
    """
    Hasta acá, todo confirma la hipótesis. **Pero el proyecto se propuso algo más ambicioso**:
    probar que la desigualdad ambiental y la desigualdad social son la misma cosa, y que eso se
    traduce en salud. Y ahí no llegamos.
    """
)

st.markdown(
    """
    <div class="card null">
        <strong>La marginación es casi idéntica en las tres zonas.</strong><br>
        Índice medio normalizado: <span class="zone-norte">Norte 0.953</span> ·
        <span class="zone-centro">Centro 0.958</span> ·
        <span class="zone-sur">Sur 0.950</span>. Las tres zonas se construyeron como grupos
        balanceados de 7 municipios, no como un gradiente social. Eso explica por qué las
        correlaciones con marginación salen débiles o nulas: <em>no había contraste que medir</em>.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card null">
        <strong>Marginación y salud respiratoria: r = −0.06 (n = 3,419 AGEBs).</strong><br>
        Prácticamente nula, y con el signo opuesto al esperado. A nivel municipal es −0.29, y
        tampoco es significativa. <strong>La tasa respiratoria sí difiere entre zonas
        (Norte 12,736 · Centro 12,615 · Sur 7,737 por 100 mil), pero sigue al gradiente
        ambiental, no al social.</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card null">
        <strong>La métrica de área verde no mide lo que su nombre sugiere.</strong><br>
        Suma los 11,739 polígonos del inventario de la SEDEMA sin filtrar por categoría. De los
        67.3 km² sumados, solo <strong>29.2 % es espacio recreativo</strong>: 42.3 % es
        vegetación dentro de instalaciones y 14.2 % son camellones de avenidas. Un camellón
        cuenta igual que un parque, y por eso la correlación con salud sale <em>positiva</em>.
        Arreglar esto es el siguiente paso, y puede cambiar el signo.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    ##### Ranking de carga integrada

    Promedio de los seis indicadores ordenado por severidad. La columna "Carga" ordena la
    tabla: **menor valor = mayor carga combinada**. Los datos se leen del archivo que exporta
    el notebook 07, no de valores escritos a mano.
    """
)


def _zone_color(val: str) -> str:
    return f"background-color: {COLORS.get(val, '#888888')}; color: white; font-weight: 600;"


_burden = pd.read_csv(DATA / "municipio_completo.csv").sort_values(
    "burden_score", ascending=True
)

df_burden = pd.DataFrame(
    {
        "Municipio": _burden["NOM_MUN"],
        "Zona": _burden["zona"],
        "LST °C": _burden["lst_mean"],
        "NDVI": _burden["ndvi_mean"],
        "NO₂ (×10⁻⁵)": _burden["no2_mean"] * 1e5,
        "PM₂.₅ µg/m³": _burden["pm25_mean"],
        "IMN": _burden["imn_mean"],
        "Tasa resp.": _burden["tasa_respiratoria"],
        "Carga (menor = peor)": _burden["burden_score"],
    }
).reset_index(drop=True)

# Styler.map replaced Styler.applymap in pandas 2.1, and applymap was removed in
# pandas 3.0 -- which is the version Streamlit Community Cloud installs.
_burden_style = df_burden.style
_zone_styler = getattr(_burden_style, "map", None) or _burden_style.applymap

st.dataframe(
    _zone_styler(_zone_color, subset=["Zona"]).format(
        {
            "LST °C": "{:.1f}",
            "NDVI": "{:.3f}",
            "NO₂ (×10⁻⁵)": "{:.1f}",
            "PM₂.₅ µg/m³": "{:.1f}",
            "IMN": "{:.3f}",
            "Tasa resp.": "{:,.0f}",
            "Carga (menor = peor)": "{:.2f}",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.markdown(
    """
    <div class="card">
        <strong>Cuauhtémoc, Azcapotzalco y Benito Juárez encabezan la carga integrada;</strong>
        Gustavo A. Madero queda 4º. El ranking está dominado por el
        <span class="zone-centro">centro</span>, empujado por el NO₂ del tráfico, y no solo por
        la periferia <span class="zone-norte">norte</span>.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ===========================================================================
# 5 — CÓMO LO MEDIMOS
# ===========================================================================
st.markdown('<div class="section-header">5. Cómo lo medimos</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(
        """
        **Fuentes**

        | Capa | Fuente | Período |
        |---|---|---|
        | Temperatura superficial | Landsat 8/9 (NASA) | 2025–2026 |
        | Vegetación (NDVI) | Landsat 8/9 | 2025–2026 |
        | NO₂ troposférico | Sentinel-5P TROPOMI (ESA) | 2025–2026 |
        | PM₂.₅ / PM₁₀ | 13 estaciones SINAICA (INECC) | 2023 y 2025 |
        | Egresos respiratorios | DGIS (Secretaría de Salud), J00–J99 | 2023 |
        | Marginación | CONAPO, índice 2020 por AGEB | 2020 |
        | Áreas verdes | Inventario SEDEMA | — |
        """
    )

with col_b:
    st.markdown(
        """
        **Dos niveles de análisis, y no son intercambiables**

        - **AGEB** (n = 3,419): la unidad más fina. Es donde se miden marginación y salud.
        - **Municipio** (n = 21): donde se integran los seis indicadores.

        Una correlación calculada en un nivel **no describe** el otro, y puede cambiar de
        signo entre ambos. Cada resultado de esta página indica su nivel y su n.

        **Las capas no son contemporáneas.** El diseño cruza variables de 2020 a 2026, lo que
        asume que el patrón espacial de cada una es estable. Es defendible para el suelo y la
        vegetación, que cambian lento; es más frágil para el NO₂, cuyo patrón se movió con el
        tráfico después de la pandemia.
        """
    )

st.divider()

# ===========================================================================
# 6 — LÍMITES
# ===========================================================================
st.markdown('<div class="section-header">6. Límites</div>', unsafe_allow_html=True)

st.markdown(
    """
    Un resultado sin sus límites no es un resultado. Estos son los que más acotan lo anterior.

    1. **La marginación no varía entre zonas** (0.950 / 0.958 / 0.953). Las zonas son grupos
       balanceados de 7 municipios, no un gradiente social. Cualquier conclusión sobre
       marginación y ambiente está limitada por esto.
    2. **La muestra municipal es chica.** Con n = 21 y 7 variables, solo 7 de los 21 pares
       tienen una correlación distinguible de cero.
    3. **La métrica de área verde suma camellones e instalaciones.** Ver sección 4.
    4. **Riesgo de falacia ecológica.** Una asociación por AGEB o por municipio no describe a
       las personas.
    5. **El nivel de la tasa respiratoria no está verificado.** La tasa ponderada por población
       es de 15,887 por 100 mil (15.9 %), demasiado alta para egresos hospitalarios en un año.
       J00–J99 incluye el resfrío común, así que la fuente puede estar contando consultas.
       Las correlaciones no dependen de que el nivel sea correcto; las cifras de nivel, sí.
    6. **El registro de PM arrastra ceros que no son mediciones.** 31 de las 60 filas
       estación-contaminante tienen media anual por debajo de 0.5 µg/m³, con mediana y
       percentil 75 en 0.000 pero miles de observaciones contadas como válidas. Tláhuac,
       Naucalpan y Ecatepec reportan media anual 0.000. Cualquier promedio que los incluya
       queda sesgado hacia abajo, y los promedios por municipio del repositorio todavía los
       incluyen: las cifras de PM por zona no son confiables hasta corregirlo.
    7. **La encuesta es un piloto.** 34 respuestas en 16 municipios, mediana de 2 por municipio.
       No es representativa y ningún resultado cuantitativo de esta página se apoya en ella.
    """
)

st.divider()

# ===========================================================================
# 7 — QUÉ SIGUE
# ===========================================================================
st.markdown('<div class="section-header">7. Qué sigue</div>', unsafe_allow_html=True)

st.markdown(
    """
    Los satélites miden el ambiente. Lo que no registran es **cómo se vive esa desigualdad**:
    cuánto tiempo pasas en el transporte, si notás el cambio de vegetación al cruzar la ciudad,
    si usás los parques que tenés cerca.

    Para eso hay una encuesta ciudadana abierta. Es la única fuente posible: no existe un
    registro público de uso del espacio público a escala de colonia.
    """
)

_c1, _c2, _c3 = st.columns(3)
for col, number, label in [
    (_c1, "34", "respuestas hasta ahora"),
    (_c2, "18", "preguntas, 5 minutos"),
    (_c3, "400", "meta para poder comparar por zona"),
]:
    with col:
        st.markdown(f'<div class="stat-number">{number}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-label">{label}</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="card">
        <strong>Faltan voces del norte y del oriente de la ciudad</strong><br>
        Con 2 respuestas por municipio no se puede comparar zonas, y esa comparación es
        justamente el objetivo. Los resultados se publicarán abiertos.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    **El siguiente arreglo técnico** es reconstruir la métrica de área verde usando solo las
    categorías recreativas (parques, plazas, jardines) y sumar una medida de accesibilidad:
    la distancia de cada AGEB al parque más cercano. Hoy tenemos 11,739 polígonos con
    categoría y geometría en el repositorio, y la métrica actual los suma todos.
    """
)

st.divider()

# ===========================================================================
# 8 — SOBRE EL PROYECTO
# ===========================================================================
st.markdown('<div class="section-header">8. Sobre el proyecto</div>', unsafe_allow_html=True)

col_about1, col_about2 = st.columns(2)

with col_about1:
    st.markdown(
        """
        **Stack**

        | Herramienta | Uso |
        |---|---|
        | Python 3.10+ | Lenguaje principal |
        | Google Earth Engine | Procesamiento satelital |
        | geopandas / shapely | Análisis espacial vectorial |
        | scipy / statsmodels / scikit-learn | Estadística, regresiones, clústeres |
        | matplotlib | Visualización estática |
        | Streamlit | Este informe |

        Este dashboard **no es interactivo**: renderiza figuras ya calculadas por el notebook
        07. Los datos agregados están en el repositorio para que cualquiera pueda recomputar
        cada número citado acá.
        """
    )

with col_about2:
    st.markdown(
        """
        **Autora**

        Nelly Itzel Rodríguez Ortiz
        Ingeniera en Computación · MSc. en Microelectrónica
        Procesamiento de señales e información aplicado a datos ambientales

        ---

        **Trabajo abierto.** El análisis completo, las limitaciones y las fuentes están en el
        repositorio. Si encontrás un error, es un aporte.
        """
    )

st.markdown(
    '<div class="citation">'
    'Proyecto de código abierto — <a href="https://github.com/nellsdev">github.com/nellsdev</a>'
    "</div>",
    unsafe_allow_html=True,
)
