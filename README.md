# 🌳 Dos Méxicos Bajo el Mismo Sol

**Desigualdad Verde, Islas de Calor y Salud Pública en la CDMX**

🚧 *Proyecto en desarrollo activo — Sprint 1/4 en progreso*

---

## 🎯 Objetivo

Evaluar la correlación entre la falta de áreas verdes, temperaturas superficiales
extremas, contaminación del aire, marginación socioeconómica, incidencia de
enfermedades respiratorias y percepción ciudadana en la Zona Metropolitana
del Valle de México.

## 🗺️ Zonas de Estudio

| Zona Nororiente | Zona Sur |
|-----------------|----------|
| San Felipe de Jesús I, GAM | Villa Coyoacán, Coyoacán |
| Valle de Aragón 1ra Secc., Neza | Chimalistac, Álvaro Obregón |
| Chamizal, Ecatepec | Jardines del Pedregal, Á.O. |

## 📊 Datos

- 🛰️ Landsat 8/9 (NDVI + LST) vía Google Earth Engine
- 💨 Calidad del aire (SIMAT)
- 🏥 Salud pública (DGIS / SINAVE)
- 📊 Censo INEGI 2020 (AGEBs)
- 🗣️ Encuesta de percepción ciudadana

## 🛠️ Stack

![Python](https://img.shields.io/badge/Python-%2314354C.svg?style=for-the-badge&logo=python&logoColor=white) · ![GoogleEarthEngine](https://img.shields.io/badge/google%20earth%20engine-%234285F4?style=for-the-badge&logo=googleearthengine&logoColor=white) · ![GeoPandas](https://img.shields.io/badge/GeoPandas--139c5a?style=for-the-badge&logo=geopandas) · ![QGIS](https://img.shields.io/badge/qgis-%2393b023?&style=for-the-badge&logo=qgis&logoColor=white) · ![Tableu](https://img.shields.io/badge/Tableu--blue?style=for-the-badge&logo=tableu) · ![Google Forms](https://img.shields.io/badge/Google%20Forms--8250df?style=for-the-badge&logo=googleforms)

## 📁 Project Structure

```
Project1-IslasCalor/
├── data/                              # Raw + processed datasets (gitignored)
├── docs/                              # Reference material
├── notebooks/                         # Thin pipeline orchestrators
│   ├── 01_exploracion_landsat.ipynb
│   └── 02_dual_visualization_no2_lst.ipynb
├── outputs/                           # Maps, charts, exported rasters
├── src/                               # Reusable Python package (installed editable)
│   ├── __init__.py                    # Public API
│   ├── config.py                      # Paths, band names, vis palettes
│   ├── aoi.py                         # Shapefile → ee.FeatureCollection
│   ├── landsat.py                     # Cloud mask + LST calibration
│   ├── sentinel5p.py                  # NO₂ quality mask + composite
│   └── visualization.py               # geemap builders
├── pyproject.toml                     # Package metadata + dependencies
├── requirements.txt                   # Pinned runtime dependencies
└── README.md
```

The `src/` package is installed in **editable mode** (`pip install -e .`), so any edit to a function is immediately reflected in every notebook — no reinstall needed.

## 🚀 How to run

### 1. Create / activate the virtual environment
```bash
cd ~/Documentos/PERSONAL/Portafolio/Project1-IslasCalor
source project1.venv/bin/activate
```

### 2. Install the package in editable mode
```bash
pip install --upgrade pip setuptools wheel
pip install -e .
```

### 3. Configure your Earth Engine project ID
Edit `src/config.py` and replace the placeholder:
```python
EE_PROJECT_ID: str = "your-gcp-project-id"
```

### 4. Launch Jupyter and open a notebook
```bash
jupyter lab
# or
jupyter notebook
```

### 5. Run the notebooks in order
| # | Notebook | What it does |
|---|---|---|
| 01 | `01_exploracion_landsat.ipynb` | Initial Landsat exploration |
| 02 | `02_dual_visualization_no2_lst.ipynb` | Dual LST + NO₂ map for CDMX |

## 🧠 Code conventions

- All reusable logic lives in `src/`. Notebooks only orchestrate the pipeline.
- Every function has a docstring (purpose, signal-processing analogy, args, returns) and type hints.
- All paths, project IDs, band names, and vis palettes are constants in `src/config.py` — no magic strings in the notebooks.
- Two time conventions: NO₂ = full year 2023; LST = summer 2023 (Jun–Aug). Update the `start_date` / `end_date` in the notebook if you want a different window.

## 📅 Roadmap

| Sprint | Semana | Meta |
|--------|--------|------|
| 🟢 Sprint 1 | 28 May – 7 Jun | Datos satelitales + encuesta |
| ⬜ Sprint 2 | 8 – 14 Jun | Datos sociales, salud e integración |
| ⬜ Sprint 3 | 15 – 21 Jun | Análisis estadístico y visualización |
| ⬜ Sprint 4 | 22 – 28 Jun | Dashboard y narrativa final |

## 👩‍💻 Autora

Nelly Itzel Rodriguez Ortiz — Ingeniera en Computación, MSc. en Microelectrónica
Especialidad: Análisis de datos y procesamiento de señales

<a href="https://www.linkedin.com/in/nellsdev/?locale=en_US"><img src="https://img.shields.io/badge/LinkedIn-Conectemos-0A66C2?style=flat-square&logo=linkedin&logoColor=white"/></a>


---
