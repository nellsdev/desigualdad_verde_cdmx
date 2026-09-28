# Dos Méxicos Under the Same Sun

**Green Inequality, Urban Heat Islands, and Air Quality in Mexico City**

[![Python](https://img.shields.io/badge/Python-3.10+-14354C.svg?logo=python&logoColor=white)](https://python.org)
[![Google Earth Engine](https://img.shields.io/badge/Earth%20Engine-4285F4?logo=googleearthengine&logoColor=white)](https://earthengine.google.com)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white)](https://jupyter.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Status:** *Sprint 3 complete* — Statistical analysis and integrated visualization.

> **Next:** *Sprint 4* — Citizen perception survey, interactive dashboard and final synthesis.


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
- **LST–NDVI correlation in the concrete belt: r = −0.829** — vegetation explains nearly 70% of the temperature gap in the most urbanized areas.

### 💨 NO₂ Pollution (Satellite — Sentinel-5P TROPOMI)

The same geography that is hotter and less green also breathes more polluted air.

- The **northern pollution belt** (Naucalpan, Tlalnepantla, GAM, Ecatepec, Nezahualcóyotl) has consistently higher NO₂ concentrations.
- **NDVI–NO₂ correlation in the north: r = −0.384** — moderate but meaningful. Less vegetation predicts more pollution.
- The **south has 30–50% lower NO₂** than the northern corridor.
- Central areas (Cuauhtémoc, Benito Juárez) also show elevated NO₂ due to traffic density — pollution does not follow a simple north-south line.

### 🌫 PM₂.₅ and PM₁₀ (Ground monitors — SINAICA)

Ground-level particulate matter confirms the satellite picture — and reveals a health crisis.

| Pollutant | North (mean) | Centre (mean) | South (mean) | WHO guideline |
|-----------|-------------|--------------|-------------|---------------|
| PM₂.₅ | 27.5 µg/m³ | 22.2 µg/m³ | 14.4 µg/m³ | 5 µg/m³ |
| PM₁₀ | 54.3 µg/m³ | 45.1 µg/m³ | 32.8 µg/m³ | 15 µg/m³ |

- **Every single station exceeds the WHO annual guideline** for PM₂.₅ and PM₁₀.
- **Gustavo A. Madero (GAM) is among the most burdened municipalities** across temperature, vegetation, NO₂, PM₂.₅ and PM₁₀ — the worst combined environmental conditions in the northern belt. On the project's full six-indicator burden score (which also includes marginalization and respiratory rate) it ranks 4th of 21; see the health section below.
- The north-south particulate divide mirrors every other indicator exactly.

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
- **Green area does not show the expected protective association.** Using total green area per
  municipality, the correlation with respiratory rate is *positive* (r = +0.52); normalising to
  green area per capita reduces it to near zero (r = +0.12, n = 20). The choice between total
  area and area per person changes the answer, and neither version supports a clean protective
  effect in this dataset.
- The integrated burden ranking (six indicators across **21** municipalities) places
  **Cuauhtémoc, Azcapotzalco and Benito Juárez** at the top — driven substantially by NO₂ from
  traffic density — rather than the northern periphery alone. The strongest and most
  consistent results in this project remain the **environmental** gradients (LST, NDVI, NO₂ and
  PM), which are mutually corroborating and measured independently of each other.

### 🔗 The Integrated Pattern

Across **five independent measurements** (LST, NDVI, NO₂, PM₂.₅, PM₁₀), the same geographic story emerges:

> **The less-green north is also the hotter north, the more polluted north, and the north with worse air quality by every metric.**

The correlation between environmental variables is so consistent that it points to a single underlying cause: **unequal distribution of green infrastructure across the metropolitan area.**

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
| **SINAICA** (INEEC) | Hourly PM₂.₅, PM₁₀, NO₂ from 13 ground monitoring stations | Notebook 04 |
| **INEGI** (Marco Geoestadístico) | Municipal boundaries (CDMX + EdoMex), AGEB-level geography | All notebooks |
| **CONAPO** | ZMVM delimitation (76 municipios); Índice de Marginación (IM_2020) by AGEB | AOI definition, Notebooks 05, 06 |
| **DGIS** (Secretaría de Salud) | Hospital discharges for respiratory diseases (ICD-10 J00–J99) by AGEB | Notebook 06 |

---

## Notebooks

Work through them in order — each builds on the previous.

| # | Notebook | What it does | Key finding |
|---|----------|-------------|-------------|
| 01 | [`01_exploration_lst.ipynb`](notebooks/01_exploration_lst.ipynb) | Land Surface Temperature map — CDMX summer vs winter | **5–10 °C gap** between north and south |
| 02 | [`02_mapping_ndvi.ipynb`](notebooks/02_mapping_ndvi.ipynb) | NDVI vegetation map — 3 zoom levels + LST-NDVI correlation | **r = −0.829** in the concrete belt |
| 03 | [`03_mapping_no2.ipynb`](notebooks/03_mapping_no2.ipynb) | NO₂ pollution map — 3 zoom levels + NDVI-NO₂ correlation | **NDVI–NO₂ r = −0.384**; north 30–50% more polluted |
| 04 | [`04_exploration_pm.ipynb`](notebooks/04_exploration_pm.ipynb) | Ground-level PM₂.₅ and PM₁₀ from 13 SINAICA stations | **All stations exceed WHO limits**; northern stations are the worst |
| 05 | [`05_marginacion.ipynb`](notebooks/05_marginacion.ipynb) | Marginalization (CONAPO IM_2020) vs. environmental variables | **IM_2020 correlates with LST** (p < 0.001); north is both hotter and more marginalized |
| 06 | [`06_salud_respiratoria.ipynb`](notebooks/06_salud_respiratoria.ipynb) | Respiratory disease × marginalization × green space | **Respiratory disease mirrors the environmental divide**; IM → health gradient is monotonic |

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
├── pyproject.toml                 # Package metadata + dependencies
├── requirements.txt               # Pinned runtime dependencies
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

## Code Conventions

- All reusable logic lives in `src/`. Notebooks only orchestrate the pipeline — no logic in notebook cells.
- Every function has a **docstring** (purpose, args, returns) and **type hints**.
- All paths, project IDs, band names, and vis palettes are constants in `src/config.py` — no magic strings in notebooks.
- Data is **fetched fresh** from Earth Engine and SINAICA on each run. Cached files go in `outputs/`.
- Time conventions: NO₂ = full year 2023; LST = summer 2023 (Jun–Aug). Update `start_date` / `end_date` in notebooks to change the window.

---

## Roadmap

| Sprint | Dates | Goal | Status |
|--------|-------|------|--------|
| 🟢 Sprint 1 | 28 May – 7 Jun | Satellite data (LST, NDVI, NO₂) + ground PM data + survey | ✅ Complete |
| 🟢 Sprint 2 | 8 – 25 Jun | Socioeconomic marginalization + health data integration | ✅ Complete |
| 🟢 Sprint 3 | 26 Jun – 9 Jul | Statistical analysis and integrated visualization | ✅ Complete |
| 🟡 Sprint 4 | 10 Jul – | Citizen perception survey, interactive dashboard and final synthesis | 🟡 In progress |

---

## Limitations

Honest scope notes. They are part of the result, not caveats to hide.

1. **Two analysis levels are mixed, and they are not interchangeable.** Environmental
   indicators (notebooks 01–04) are analysed across the full ZMVM. Social and health indicators
   (notebooks 05–07) are analysed at two different levels: AGEB (n = 3,419) and municipality
   (n = 21). Correlations computed at these levels are not comparable and can differ in sign.
   Every correlation reported above states its level and n.
2. **Small municipality sample.** With n = 21 municipalities and 7 variables, most
   municipality-level correlations are not statistically distinguishable from zero. Those
   values are reported for transparency, not as established effects.
3. **Correlation is not causation.** LST, NDVI and NO₂ co-vary strongly with each other, so
   their individual contributions cannot be separated without a multivariate design.
4. **Green-area metric sensitivity.** Results change materially between total green area (m²)
   and green area per capita. Total area conflates municipality size with green access;
   per-capita is the more defensible metric and is used where stated.
5. **Ecological fallacy risk.** AGEB- and municipality-level associations do not describe
   individuals. A marginalization–health relationship that appears or disappears at one level
   may not hold at another.
6. **Respiratory data coverage.** Hospital discharge records (DGIS, ICD-10 J00–J99) are
   available only for a subset of ZMVM municipalities, which constrains the health analysis to
   the Periferia Zone and reduces the effective sample.
7. **Zone definitions.** The three-zone partitioning (Norte / Centro / Sur) used in notebooks
   05–07 is a balanced analytical grouping of 7 municipalities each. It does not correspond
   exactly to the geographic belt description used for the satellite analysis in notebooks
   01–04, and the two must not be read as the same partition.
8. **Survey sample.** The citizen perception survey (n = 38) is a pilot and is not
   statistically representative of the metropolitan area. No quantitative claim in this README
   rests on it.

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
