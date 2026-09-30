# Dos Méxicos Under the Same Sun

**Green Inequality, Urban Heat Islands, and Air Quality in Mexico City**

[![Python](https://img.shields.io/badge/Python-3.10+-14354C.svg?logo=python&logoColor=white)](https://python.org)
[![Google Earth Engine](https://img.shields.io/badge/Earth%20Engine-4285F4?logo=googleearthengine&logoColor=white)](https://earthengine.google.com)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white)](https://jupyter.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Status:** *Sprint 3 complete* — Statistical analysis and integrated visualization.

> **Next:** *Sprint 4* — Citizen perception survey, dashboard and final synthesis.


---

## The Problem

The Zona Metropolitana del Valle de México (ZMVM) is one of the world's largest urban areas — 22 million people across 76 municipalities. But the city is not uniform: some neighborhoods have tree-lined streets, parks, and cool air, while others have concrete, asphalt, and exhaust fumes.

**Is the environmental divide in Mexico City measurable from space? Does it match ground-level pollution? And who bears the highest combined burden?**

This project answers those questions with data.

---

## Key Findings

### 🌡️ Land Surface Temperature (LST)

The northern ZMVM is **5–10 °C hotter** than the south — in both summer and winter.

- **Nororiente mean:** ~35 °C (summer), ~28 °C (winter)
- **South mean:** ~27 °C (summer), ~20 °C (winter)
- The gap persists across seasons, proving it is structural, not meteorological.

### 🌿 Vegetation (NDVI)

The north has **significantly less vegetation** — and the correlation with temperature is near-perfect in the concrete belt.

- **Nororiente mean NDVI:** 0.12 (barely above "sparse vegetation")
- **South mean NDVI:** 0.33 (moderate / healthy vegetation)
- **LST–NDVI correlation in the concrete belt: r = −0.829** (notebook 02, belt subset — the 21-municipality matrix in notebook 07 gives r = −0.936) — vegetation accounts for roughly 70% of the temperature variance in the most urbanized areas.

### 💨 NO₂ Pollution (Satellite — Sentinel-5P TROPOMI)

The same geography that is hotter and less green also breathes more polluted air.

- The **northern pollution belt** (Naucalpan, Tlalnepantla, GAM, Ecatepec, Nezahualcóyotl) has consistently higher NO₂ concentrations.
- **NDVI–NO₂ correlation in the north: r = −0.384** — moderate but meaningful. Less vegetation predicts more pollution.
- The **south has 30–50% lower NO₂** than the northern corridor.
- Central areas (Cuauhtémoc, Benito Juárez) also show elevated NO₂ due to traffic density — pollution does not follow a simple north-south line.

### 🌫 PM₂.₅ and PM₁₀ (Ground monitors — SINAICA)

Ground-level particulate matter confirms the satellite picture — and reveals a health crisis.

| Pollutant | Norte (mean) | Centro (mean) | Sur (mean) | WHO annual guideline |
|-----------|-------------|--------------|-------------|---------------|
| PM₂.₅ | 20.2 µg/m³ | 18.3 µg/m³ | 15.9 µg/m³ | 5 µg/m³ |
| PM₁₀ | 40.5 µg/m³ | 34.4 µg/m³ | 29.9 µg/m³ | 15 µg/m³ |

- **Every station with valid data exceeds the WHO annual guideline** — PM₂.₅ 13 of 13, PM₁₀ 16 of
  16. Reaching that sentence required cleaning the series; see Limitations item 13.
- **Gustavo A. Madero (GAM) is among the most burdened municipalities** across temperature, vegetation, NO₂, PM₂.₅ and PM₁₀ — the worst combined environmental conditions in the northern belt. On the project's full six-indicator burden score (which also includes marginalization and respiratory rate) it ranks 4th of 21; see the health section below.
- The north–south particulate divide holds for both pollutants, though the PM₂.₅ spread between
  zones is narrow (4.3 µg/m³) next to the temperature gap.

### 🧭 Marginalization and the Urban Heat Divide

Socioeconomic marginalization is not evenly distributed, and it tends to co-occur with
environmental burden — though this association is weaker than the environmental signal itself.

- **Marginalization (IM_2020) is positively, but not significantly, associated with LST at
  municipality level** (r = +0.30, n = 21, p ≈ 0.19). The direction matches the hypothesis;
  with only 21 municipalities the effect cannot be established statistically.
- When grouped by actual temperature and green cover (rather than geography), the "Hot zone"
  (dense, paved, low vegetation) shows **higher marginalization** than the "Cool zone".
- The north–south temperature divide overlaps with a **north–south social vulnerability
  divide**, but the two are not identical: central boroughs such as Cuauhtémoc carry very high
  environmental burden without high marginalization.

### 🏥 Respiratory Health: A Weaker Signal Than Hypothesised

The project's most ambitious hypothesis was that environmental and social divides translate
into respiratory health outcomes. The data only partially supports it, and reporting that
honestly matters as much as reporting the positive findings.

- **At AGEB level (n = 3,419), marginalization and respiratory discharge rate are essentially
  uncorrelated** (r = −0.06). At municipality level the association is also weak and negative
  (r = −0.29, n = 21).
- Grouping AGEBs by CONAPO marginalization grade does **not** produce a monotonic gradient.
  Median discharge rates per 100k are 17,266 (Muy bajo), 14,153 (Bajo), 16,066 (Medio) and
  21,961 (Alto). Only the highest grade stands clearly above the others, and the ordering
  between the lower grades is not stable.
- **Green area, tested properly, turns out to be negligible either way** — see the next section.
  The inventory metric was unusable outside CDMX (Limitations 7), so the question was re-run
  with satellite NDVI, which has full coverage.
- The integrated burden ranking (six indicators across **21** municipalities) places
  **Cuauhtémoc, Azcapotzalco and Benito Juárez** at the top — driven substantially by NO₂ from
  traffic density — rather than the northern periphery alone. The strongest and most
  consistent results in this project remain the **environmental** gradients (LST, NDVI, NO₂ and
  PM), which are mutually corroborating and measured independently of each other.

### 🌿 Vegetation and Social Outcomes at AGEB Level

This is the project's original question, and it had never been tested validly: the only
per-AGEB green variable was the SEDEMA inventory, which covers just the 16 CDMX alcaldías.
NDVI has full coverage, so it was computed for every AGEB — the mean over a 250 m buffer around
each AGEB centroid, summer 2025 — and frozen to `dashboards/data/ndvi_ageb_2025.csv` so the
number can be recomputed by anyone.

Baseline, on the full sample:

| Relationship | r | n | p | R² |
|---|---|---|---|---|
| NDVI ↔ marginalization (CONAPO IM_2020) | **−0.087** | 3,419 | < 0.001 | 0.8 % |
| NDVI ↔ respiratory discharge rate | **+0.117** | 3,419 | < 0.001 | 1.4 % |

**Neither survives a robustness check, and neither is worth acting on.**

- **Both are negligible.** At n = 3,419 a correlation of 0.09 clears p < 0.001 without effort.
  Vegetation explains under 1.5 % of the variance in either outcome.
- **The health sign does not hold.** Excluding AGEBs with fewer than 1,000 residents, r moves
  from +0.117 to −0.023 (not significant); with a 5,000 floor it is −0.267. Controlling for
  log(population) gives −0.075. The positive baseline is a small-area artifact.
- **The marginalization sign is method-dependent.** Pearson gives −0.087, Spearman's rank
  correlation gives **+0.148**, and the partial correlation controlling for population gives
  −0.140. The linear and the rank relationship point in opposite directions.
- **The reason is a confound that this design cannot separate.** NDVI is correlated with AGEB
  population (r = −0.217): small AGEBs are peripheral and green (mean NDVI 0.170 under 500
  residents, against 0.098 above 5,000) and differ from dense central AGEBs in many other ways.
- **NDVI by zone** (median): Norte 0.088 (n = 1,409), Centro **0.087** (n = 1,303), Sur 0.143
  (n = 707). Norte and Centro are indistinguishable; only the south is meaningfully greener,
  which is why the north–south story holds for temperature but not for everything else.

The honest result is that **the original question is not answered by this design.** An areal mean
of greenness over an AGEB conflates vegetation with density. Separating the two needs either a
density-stratified design or a distance-based accessibility measure — how far is the nearest
park — instead of an average over the polygon.

### 🔗 The Integrated Pattern

Across **five independent measurements** (LST, NDVI, NO₂, PM₂.₅, PM₁₀), the same geographic story emerges:

> **The less-green north is also the hotter north, the more polluted north, and the north with worse air quality by every metric.**

The correlation between environmental variables is so consistent that it points to a common underlying factor: **the unequal distribution of green infrastructure across the metropolitan area.** This remains a hypothesis rather than a demonstrated cause — see Limitations.

---

## Study Area

The Zona Metropolitana del Valle de México (ZMVM): 16 CDMX boroughs + 60 Estado de México municipalities.

Notebooks 01–05 analyze the full ZMVM. Notebook 06 narrows the AOI to **21 municipios** (the Periferia Zone: 16 CDMX alcaldías + 5 northern EdoMex municipios) to match the available respiratory health data.

For comparative analysis, the area is divided into three zones:

| Zone | Colour | Constituents | Character |
|------|--------|-------------|-----------|
| **Norte (nororiente)** | 🔴 Red | Ecatepec, Nezahualcóyotl, GAM, Tlalnepantla, Naucalpan, Iztapalapa | Dense urban-industrial, low vegetation |
| **Centro** | 🟠 Orange | Cuauhtémoc, Benito Juárez | Dense mixed-use, heavy traffic |
| **Sur** | 🟢 Green | Coyoacán, Tlalpan, Álvaro Obregón, Xochimilco, La Magdalena Contreras, Cuajimalpa | Residential with forest cover |

---

## Data Sources

| Source | What we get | Used in |
|--------|------------|---------|
| **Landsat 8/9** (NASA–USGS) | Land Surface Temperature (LST) in °C, NDVI | Notebooks 01, 02 |
| **Sentinel-5P TROPOMI** (ESA) | Tropospheric NO₂ column (mol/m²) | Notebook 03 |
| **SINAICA** (INECC) | Hourly PM₂.₅, PM₁₀, NO₂ from 20 stations; readings flagged invalid by the source are dropped | Notebook 04 |
| **INEGI** (Marco Geoestadístico) | Municipal boundaries (CDMX + EdoMex), AGEB-level geography | All notebooks |
| **CONAPO** | ZMVM delimitation (76 municipios); Índice de Marginación (IM_2020) by AGEB | AOI definition, Notebooks 05, 06 |
| **DGIS** (Secretaría de Salud) | Hospital discharges for respiratory diseases (ICD-10 J00–J99) by AGEB | Notebook 06 |

Committed derivations, so every number in this README can be recomputed without re-running the
pipeline:

| File | What it holds |
|---|---|
| `dashboards/data/municipio_completo.csv` | per-municipality indicators behind the burden ranking |
| `dashboards/data/ageb_data.csv` | per-AGEB marginalization, health and inventory green area |
| `dashboards/data/ndvi_ageb_2025.csv` | **NDVI per AGEB** (250 m buffer, summer 2025) — the vegetation test |
| `dashboards/data/correlation_matrix.csv` | the matrix plotted in the figures |

---

## Notebooks

Work through them in order — each builds on the previous.

| # | Notebook | What it does | Key finding |
|---|----------|-------------|-------------|
| 01 | [`01_exploration_lst.ipynb`](notebooks/01_exploration_lst.ipynb) | Land Surface Temperature map — CDMX summer vs winter | **5–10 °C gap** between north and south |
| 02 | [`02_mapping_ndvi.ipynb`](notebooks/02_mapping_ndvi.ipynb) | NDVI vegetation map — 3 zoom levels + LST-NDVI correlation | **r = −0.829** in the concrete belt (belt subset; 21-municipality matrix: −0.936) |
| 03 | [`03_mapping_no2.ipynb`](notebooks/03_mapping_no2.ipynb) | NO₂ pollution map — 3 zoom levels + NDVI-NO₂ correlation | **NDVI–NO₂ r = −0.384**; north 30–50% more polluted |
| 04 | [`04_exploration_pm.ipynb`](notebooks/04_exploration_pm.ipynb) | Ground-level PM₂.₅ and PM₁₀ from 13 SINAICA stations | **All stations exceed WHO limits**; northern stations are the worst |
| 05 | [`05_marginacion.ipynb`](notebooks/05_marginacion.ipynb) | Marginalization (CONAPO IM_2020) vs. environmental variables | **IM_2020 vs. LST: r = +0.30, not significant at n = 21**; the north is both hotter and more marginalized |
| 06 | [`06_salud_respiratoria.ipynb`](notebooks/06_salud_respiratoria.ipynb) | Respiratory disease × marginalization × green space | **Respiratory health does not follow the environmental gradient** (r = −0.06 at AGEB level); see Limitations |

---

## Project Structure

```
Project1-IslasCalor/
├── data/                          # Raw + processed datasets (gitignored)
│   └── raw/
│       └── shapefiles/            # INEGI shapefiles (09_cdmx, 15_mexico)
├── notebooks/                     # Jupyter notebook orchestrators
│   ├── 01_exploration_lst.ipynb   # Land Surface Temperature analysis
│   ├── 02_mapping_ndvi.ipynb      # Vegetation index (NDVI) analysis
│   ├── 03_mapping_no2.ipynb       # Satellite NO₂ pollution mapping
│   ├── 04_exploration_pm.ipynb    # Ground-level PM₂.₅ / PM₁₀ analysis
│   ├── 05_marginacion.ipynb       # Marginalization × heat analysis
│   └── 06_salud_respiratoria.ipynb# Respiratory health × environment × marginalization
├── src/                           # Reusable Python package (installed editable)
│   ├── __init__.py                # Public API — re-exports all modules
│   ├── config.py                  # Paths, EE project ID, band names, vis palettes
│   ├── aoi.py                     # Shapefile → ee.FeatureCollection loaders
│   ├── landsat.py                 # Cloud mask + LST + NDVI composites
│   ├── sentinel5p.py              # NO₂ quality mask + composite
│   ├── visualization.py           # geemap builders (dual + triple maps)
│   ├── air_quality.py             # SINAICA data API (NO₂, PM₂.₅, PM₁₀)
│   ├── stations.py                # Station metadata, zones, WHO limits
│   └── plot_utils.py              # Matplotlib helpers (zone colours, WHO lines)
├── outputs/                       # Maps, charts, exported rasters
├── docs/                          # Reference material
├── encuesta/                      # Citizen perception survey
├── presentación/                  # Presentation materials
├── pyproject.toml                 # Package metadata + the analysis dependency stack
├── requirements.txt               # Deploy-time dependencies for the dashboard only
└── README.md                      # This file
```

The `src/` package is installed in **editable mode** (`pip install -e .`), so edits to any function are immediately reflected in every notebook — no reinstall needed.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Geospatial processing | Google Earth Engine (`earthengine-api`) |
| Interactive maps | `geemap` (folium-based) |
| Geospatial vector | `geopandas`, `shapely` |
| Data analysis | `pandas`, `numpy` |
| Visualization | `matplotlib` |
| HTTP data access | `requests` (SINAICA API) |
| Environment | Jupyter Lab, `ipykernel` |

---

## Setup

### 1. Create and activate the virtual environment

```bash
cd Project1-IslasCalor
python3 -m venv project1.venv
source project1.venv/bin/activate
```

### 2. Install the package in editable mode

```bash
pip install --upgrade pip setuptools wheel
pip install -e .
```

### 3. Configure Earth Engine

1. Go to [code.earthengine.google.com](https://code.earthengine.google.com) and register a project.
2. Enable the Earth Engine API for your GCP project.
3. Authenticate: `earthengine authenticate`
4. Set your project ID in `src/config.py`:
   ```python
   EE_PROJECT_ID: str = "your-gcp-project-id"
   ```

### 4. Run Jupyter

```bash
jupyter lab
```

Open the notebooks in `notebooks/` and run them in order (01 → 02 → 03 → 04 → 05 → 06).

---

## Dashboard

A Streamlit report that renders the project's map gallery and the municipality summary table.

**It is a styled static report, not an interactive dashboard.** There are no filters,
selectors or parameter controls — the app contains six `st.image` calls and one `st.dataframe`.
Every figure is pre-rendered by notebook 07 and committed to `outputs/graficos/`, so the app
needs neither the analysis stack nor Earth Engine access to run.

```bash
streamlit run dashboards/app.py
```

`dashboards/data/*.csv` holds the aggregated tables that notebook 07 exports. **The app does not
read them** — they are committed so that every correlation reported in this README can be
recomputed from the repository without re-running the pipeline.

Deploy dependencies live in `requirements.txt` (streamlit, pandas, numpy). The analysis stack
lives in `pyproject.toml` and is installed with `pip install -e .`.

---

## Code Conventions

- All reusable logic lives in `src/`. Notebooks only orchestrate the pipeline — no logic in notebook cells.
- Every function has a **docstring** (purpose, args, returns) and **type hints**.
- All paths, project IDs, band names, and vis palettes are constants in `src/config.py` — no magic strings in notebooks.
- Data is **fetched fresh** from Earth Engine and SINAICA on each run. Cached files go in `outputs/`.
- Time conventions: the environmental layers are pulled for the 2025–2026 window (see the
  `start_date` / `end_date` arguments in notebooks 01–04). The social and health layers are
  fixed by their sources: DGIS discharges for 2023 and CONAPO marginalization for 2020.
  Changing the environmental window is a one-line edit; changing the social window is not.

---

## Roadmap

| Sprint | Dates | Goal | Status |
|--------|-------|------|--------|
| 🟢 Sprint 1 | 28 May – 7 Jun | Satellite data (LST, NDVI, NO₂) + ground PM data + survey | ✅ Complete |
| 🟢 Sprint 2 | 8 – 25 Jun | Socioeconomic marginalization + health data integration | ✅ Complete |
| 🟢 Sprint 3 | 26 Jun – 9 Jul | Statistical analysis and integrated visualization | ✅ Complete |
| 🟡 Sprint 4 | 10 Jul – | Citizen perception survey, dashboard and final synthesis | 🟡 In progress |

---

## Limitations

Honest scope notes. They are part of the result, not caveats to hide. Items 1–3 are the ones
that shaped the design; the rest bound how far the results can be pushed.

1. **Two analysis levels are used and they are not interchangeable.** Environmental indicators
   (notebooks 01–04) are analysed across the full ZMVM. Social and health indicators are
   analysed at two different levels: AGEB (n = 3,419) and municipality (n = 21). Correlations
   computed at these levels answer different questions about different units, are not
   comparable, and can differ in sign. Every correlation reported above states its level and n.
2. **The variables are not contemporaneous.** The dataset spans 2020 to 2026:

   | Layer | Period | Source |
   |---|---|---|
   | Land surface temperature, NDVI | 2025–2026 | Landsat 8/9 |
   | Tropospheric NO₂ | 2025–2026 | Sentinel-5P TROPOMI |
   | Ground PM₂.₅ / PM₁₀ | 2023 and 2025 | SINAICA |
   | Respiratory hospital discharges | 2023 | DGIS |
   | Marginalization index | 2020 | CONAPO (2020 census) |

   The design therefore assumes that the spatial pattern of each variable is stable across that
   window. That is defensible for surface materials and green cover, which change slowly, but it
   is an assumption rather than a tested fact, and it is weakest for NO₂, whose spatial pattern
   shifted with post-pandemic traffic. The marginalization index derives from the March 2020
   census, collected at the onset of the pandemic.
3. **The study extent changed during the project.** Notebooks 01–05 analyse the full ZMVM
   (76 municipalities). Notebook 06 narrowed the area to a 21-municipality Periferia zone,
   because that is where the available health and marginalization data overlap. The narrowing
   was driven by data availability rather than by the research question, and the two extents
   are not directly comparable.
4. **Small municipality sample.** With n = 21 municipalities and 7 variables, most
   municipality-level correlations are not statistically distinguishable from zero — only 7 of
   the 21 pairs are significant at p < 0.05. Those values are reported for transparency, not as
   established effects.
5. **Norte / Centro / Sur is an analytical grouping, not a geography.** The three zones are a
   balanced partition of 7 municipalities each. Only two of the seven "Centro" municipalities
   (Cuauhtémoc and Benito Juárez) are central; the others were assigned to balance group sizes.
   The grouping does not describe concentric urban rings and must not be read as if it did. It is
   also not the same partition as the geographic belt used for the satellite analysis in
   notebooks 01–04.
6. **Correlation is not causation.** LST, NDVI and NO₂ co-vary strongly with each other, so
   their individual contributions cannot be separated without a multivariate design.
7. **The green-area metric is not usable outside CDMX, and does not measure recreational
   space.** `area_verde_total_m2` sums the SEDEMA green-area inventory intersecting each AGEB,
   with two independent defects:

   *Coverage.* The inventory covers **only the 16 CDMX alcaldías** (`cve_delg` runs 1–16). The
   five Estado de México municipios in the study area have essentially no recorded green area:
   Coacalco 0 m², Ecatepec 5,581 m², Tlalnepantla 137,973 m² and Naucalpan 642,124 m², against a
   median of **5.35 km² for the CDMX alcaldías**. That is a coverage gap, not an absence of
   parks, and it invalidates any ZMVM-wide correlation involving this column. Those five
   municipios all fall in the Norte zone.

   *Category.* Of the 67.2 km² summed, only **29.3 % is recreational** (parks, alamedas, plazas,
   gardens); 42 % is vegetation inside urban facilities (school grounds, housing units,
   assistance centres) and 14 % is road verges and medians. A camellón along an avenue counts as
   much as a park.

   Filtering to recreational categories does flip the AGEB-level sign (+0.013 → −0.011), which
   confirms the category defect — but every correlation remains indistinguishable from zero, and
   the coverage gap cannot be filtered away. **`area_verde_total_m2` should not be used for the
   21-municipality analysis.** The measure with full ZMVM coverage is **NDVI from Landsat**. At
   municipality level it gives r = −0.301 with respiratory rate and r = −0.372 with
   marginalization (n = 21, neither significant). Computed per AGEB instead — the test that
   matters, because that is where the health data lives — the baseline is r = +0.117 and
   r = −0.087 (n = 3,419), but **neither survives a robustness check**: the health sign reverses
   under a population floor, and the marginalization sign reverses under a rank correlation. NDVI
   is itself correlated with AGEB population (r = −0.217), so an areal mean cannot separate
   vegetation from density. See the vegetation section above.
8. **Ecological fallacy risk.** AGEB- and municipality-level associations do not describe
   individuals. A marginalization–health relationship that appears or disappears at one level
   may not hold at another.
9. **Respiratory data coverage.** Hospital discharge records (DGIS, ICD-10 J00–J99) are
   available only for a subset of ZMVM municipalities, which constrains the health analysis to
   the Periferia Zone and reduces the effective sample.
10. **The level of the respiratory rate has not been verified.** The population-weighted rate is
    15,887 per 100,000 (15.9%). That is implausibly high for hospital *discharges* over a single
    year. ICD-10 J00–J99 includes the common cold (J00) and other upper-respiratory conditions,
    so the source figure may be counting outpatient episodes rather than discharges. This must be
    checked against the DGIS data dictionary before any health *level* is quoted; the
    correlation results do not depend on the level being correct, only on the ranking.
11. **Survey sample.** The citizen perception survey has **34 responses spread over 16
    municipalities** — a median of 2 per municipality. It is a pilot, it is not statistically
    representative at any geographic level used in this README, and no quantitative claim here
    rests on it. Two further constraints: 4 of the 16 municipalities named by respondents
    (Zumpango, Atizapán de Zaragoza, Nicolás Romero, La Paz) fall outside the 21-municipality
    Periferia zone used for the analysis, and analysing the perception items by zone would need
    at least an order of magnitude more responses.
12. **One figure is not yet reproduced.** The `r = −0.829` LST–NDVI correlation reported for the
    concrete belt comes from notebook 02, which samples 400 pixels through Earth Engine and does
    not persist them. It cannot currently be re-derived from the exported files in this
    repository, and the municipality-level matrix gives a different value (−0.936) for a
    different sample. Treat the belt figure as provisional until the sample is written to disk
    and the value is frozen.
13. **The PM series needed cleaning, and the cleaning is a judgement call.** SINAICA flags every
    reading with `validoAct`, which the pipeline computed as `is_valid` and then **ignored**: the
    annual mean averaged over invalid readings, which is why several stations reported a mean of
    0.000 µg/m³ for a year. Filtering on the flag removes those, but not all of them — Ecatepec
    PM₁₀ reports a flat 0.000 series with the valid flag set for all 8,760 hours, which is
    physically impossible in this basin. The rule applied is: at least 2,190 valid readings
    (25 % of the year), and at least 25 % of valid readings above zero. That drops exactly three
    series — Ecatepec PM₁₀, Miguel Hidalgo PM₁₀ and Miguel Hidalgo PM₂.₅ (one valid hour each) —
    and leaves every other station's mean unchanged. Occasional zeros inside an otherwise normal
    series are real and are kept.

---

## Author

**Nelly Itzel Rodríguez Ortiz** — Computer Engineer, MSc. in Microelectronics  
Data analysis and signal processing specialist  

<a href="https://www.linkedin.com/in/nellsdev/?locale=en_US">
  <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin&logoColor=white"/>
</a>

---

## License

MIT — see [LICENSE](LICENSE)
