# Tribal Fire Science & Indigenous Data Sovereignty

> Jupyter notebooks and shared Python modules for analyzing wildfire history, risk, and stewardship on and near Tribal lands in the United States, built with real data, modular code, and OCAP®-aligned data governance.

**Authors:** Lilly Jones, PhD (Daear Consulting, LLC)
**Version:** 1.0.0 · Released February 2026  
**License:** See [LICENSE](LICENSE)  
**Citation:** See [citation.cff](citation.cff) or the [cite this repo](#citation) section below

[![DOI](https://zenodo.org/badge/1170268849.svg)](https://doi.org/10.5281/zenodo.19265139)

## Why This Repo Exists
Tribal nations face disproportionate wildfire risk, yet most fire science tools and datasets are built without Tribal input and applied without Tribal oversight. This project exists to change that by providing open, reproducible, and sovereignty-conscious tools for Tribal-led fire research and land management.

All analysis uses real, documented public data sources. No synthetic data. All code is modular and designed to be extended by Tribal colleges, land managers, and researchers working at the intersection of Indigenous data sovereignty and fire science.

## Notebooks
| Notebook | Description |
|---|---|
| `historical_fast_fires_tribal.ipynb` | Historical wildfire analysis (MTBS 1984–present) on and near Tribal lands (frequency, severity, and risk scores) by tribe |
| `fast_fire_days_analysis.ipynb` | Identifies and analyzes days with rapid fire growth using weather and fire occurrence data |
| `community_assets_at_risk.ipynb` | Maps Tribal community assets (infrastructure, housing, cultural sites) within fire risk zones |
| `tribal_wui_pressure_index.ipynb` | Quantifies Wildland-Urban Interface pressure on Tribal lands using WUI and fire perimeter data |
| `tribal_fire_capacity_analysis.ipynb` | Assesses fire suppression and response capacity across Tribal nations |
| `jurisdictional_complexity_analysis.ipynb` | Analyzes overlapping federal, state, and Tribal fire jurisdictions and their management implications |
| `indigenous_fire_stewardship.ipynb` | Documents and contextualizes Indigenous prescribed fire traditions and their relationship to modern fire management |
| `fire_weather_monitoring_gaps.ipynb` | Quantifies RAWS monitoring coverage relative to Tribal land, identifies monitoring dead zones, and provides a coverage gap score for federal investment in Tribal fire weather infrastructure |
| `cross_tribal_collaboration.ipynb` | Identifies opportunities for inter-tribal fire management coordination based on shared risk and geography |
| `climate_projections_tribal_fire_weather.ipynb` | Analyze fire history, capacity gaps, and structural risk based on current and historical conditions |
| `postfire_watershed_vulnerability.ipynb` | Burned watersheds are highly vulnerable to erosion, debris flows, and drinking water contamination. Tribal Nations in headwater areas face compounding risks when fire burns upstream of water supply infrastructure |
| `smoke_air_quality_exposure.ipynb` | Wildfire smoke measured as fine particulate matter (PM2.5) is a direct, measurable public health impact that connects fire science to community health outcomes |

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/daearconsulting/tribal_fire_science.git
cd tribal_fire_science
```

### 2. Create the conda environment
```bash
conda env create -f environment.yaml
conda activate tribal-fire-science
```

### 3. Register the Jupyter kernel
```bash
python -m ipykernel install --user --name tribal-fire-science \
  --display-name "Python (tribal-fire-science)"
```

### 4. Open in VSCode
- File  Open Folder  `tribal_fire_science`
- `Ctrl+Shift+P` **Python: Select Interpreter**  `tribal-fire-science`

### 5. Run your first notebook
Open `notebooks/historical_fast_fires_tribal.ipynb` and run all cells.
The Census TIGER tribal boundaries will download and cache automatically on first run.

## Data Setup
| Dataset | How to obtain | Loader |
|---|---|---|
| Census TIGER AIANNH | Auto-downloads on first run | `loaders.load_census_aian()` |
| NIFC Fire Perimeters | Auto-downloads on first run | `loaders.load_nifc_perimeters()` |
| MTBS Burned Areas | **Manual download required** - see below | `loaders.load_mtbs_perimeters()` |
| BIA Tribal Boundaries | Auto-downloads on first run | `loaders.load_bia_tribal_boundaries()` |
| Native Land Digital | Auto-downloads on first run (CC BY-NC 4.0) | `loaders.load_native_land_territories()` |
| FEMA National Risk Index | Auto-downloads on first run | `loaders.load_fema_national_risk_index()` |
| WUI Dataset | **Manual download required** - see below | `loaders.load_wui()` |
| NOAA Climate Data | Requires free API token - see below | `loaders.load_noaa_climate_data()` |

All cached data is stored in `data/cache/` and `data/raw/` and both are gitignored and never committed to the repo.

### MTBS Manual Download
1. Go to [https://www.mtbs.gov/direct-download](https://www.mtbs.gov/direct-download)
2. Download the national fire perimeters shapefile
3. Extract and place at: `data/raw/mtbs_perimeters/mtbs_perims_DD.shp`

### WUI Manual Download
1. Go to [https://www.fs.usda.gov/rds/archive/catalog/RDS-2015-0047-2](https://www.fs.usda.gov/rds/archive/catalog/RDS-2015-0047-2)
2. Download and extract to: `data/raw/wui/`

### NOAA API Token
1. Request a free token at [https://www.ncei.noaa.gov/cdo-web/token](https://www.ncei.noaa.gov/cdo-web/token)
2. Create a `.env` file at repo root (never commit this):
```
NOAA_CDO_TOKEN=your_token_here
```

## Repository Structure

```
tribal_fire_science/
├── notebooks/               # One notebook per analysis topic
├── src/                     # Shared Python modules
│   ├── __init__.py          # Exposes REPO_ROOT
│   ├── data/
│   │   ├── constants.py     # Paths, CRS, source URLs, thresholds
│   │   ├── loaders.py       # Fetch and cache functions for every dataset
│   │   └── validators.py    # Data integrity checks: no synthetic fallbacks
│   ├── viz/
│   │   ├── styles.py        # Color palettes, design tokens, mpl rcParams
│   │   ├── maps.py          # Folium base maps, tribal layers, choropleths
│   │   └── charts.py        # Timeline bars, heatmaps, scatter plots
│   ├── geo/
│   │   └── utils.py         # CRS helpers, spatial joins, area calculations
│   └── indigenous/
│       └── sovereignty.py   # OCAP® governance, attribution, TEK disclaimer
├── data/
│   ├── raw/                 # Downloaded source files (gitignored)
│   ├── interim/             # Intermediate processed files (gitignored)
│   ├── final/               # Analysis-ready files (gitignored)
│   └── cache/               # API response cache (gitignored)
├── outputs/                 # Figures and exported CSVs (gitignored)
├── environment.yaml         # Conda environment (Python 3.11)
├── workflows.md             # Tribal fire research workflow reference
└── citation.cff             # Citation metadata
```

### Importing `src` in Notebooks

```python
import sys
from pathlib import Path

REPO_ROOT = Path().resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data import constants, loaders, validators
from src.viz import maps, charts, styles
from src.geo import utils as geo_utils
from src.indigenous.sovereignty import print_data_acknowledgment
```

## Workflows
This repo supports the following Tribal fire research and management workflows.
See [`workflows.md`](workflows.md) for full detail on inputs, steps, and tools for each.

| Workflow | Purpose |
|---|---|
| Historical Fire Analysis and Risk Mapping | Understand past fire behavior to predict future risk |
| Fire Behavior Simulation | Model fire spread using FARSITE/FlamMap under varying conditions |
| Fire Impact on Cultural and Ecological Resources | Protect sacred sites, heritage areas, and ecocultural plants |
| Real-Time Fire Monitoring and Early Warning | Track active fires and generate dynamic risk alerts |
| Prescribed Burn Planning and Optimization | Support controlled burns for ecosystem restoration |
| Climate Change & Fire Regime Projection | Assess how shifting climate affects Tribal fire risk |
| Multi-Scale Decision Support Dashboard | Centralize fire data for Tribal land management decisions |

## Data Sovereignty
This project is guided by three complementary data governance frameworks:

**OCAP®** (First Nations Information Governance Centre): Tribal Nations own, control, access, and possess data about their own communities and territories. [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/)

**CARE** (Global Indigenous Data Alliance): Data use must deliver Collective Benefit to Indigenous peoples, respect their Authority to Control, uphold Responsibility to communities, and center Ethics across the full data lifecycle. [https://www.gida-global.org/care](https://www.gida-global.org/care)

**FAIR** (FORCE11): Data is Findable, Accessible, Interoperable, and Reusable. FAIR governs technical data standards; CARE and OCAP® govern the ethical obligations to Tribal Nations that FAIR alone does not address. [https://www.go-fair.org/fair-principles/](https://www.go-fair.org/fair-principles/)

We recognize that:
- Tribal Nations are sovereign governments with the right to control data about their own communities and territories
- Federal and third-party boundaries (Census, BIA) are for analysis only and do not represent Tribal self-definition of territory
- Traditional Ecological Knowledge belongs to the communities that hold it and is not treated as extractable data
- This work is intended to support Tribal-led fire science

`src/indigenous/sovereignty.py` contains data attribution metadata, OCAP®/CARE/FAIR governance notes per dataset, and a TEK disclaimer. Call `print_data_acknowledgment()` at the top of every notebook that uses Tribal data sources.

## Citation
If you use this software, please cite it as:

```
Jones, L., & Sanovia, J. (2026). Tribal Fire Science (Version 1.0.0).
https://doi.org/10.5281/zenodo.19265139
https://orcid.org/0009-0003-0022-1452 · https://orcid.org/0000-0002-7127-2084
```

Or see [`citation.cff`](citation.cff) for machine-readable citation metadata.

## Acknowledgments
This work adheres to Tribal data sovereignty principles. We gratefully acknowledge the nations whose lands and fire histories are represented in these analyses, and whose knowledge systems inform this work far beyond what any dataset can capture. We gratefully acknowledge the Tribal data sovereignty work by Tribal members and thought leaders, including the authors of CARE, FAIR, OCAP®, Local Contexts, and IEEE 2890-2025.  

Developed by Lilly Jones, PhD ([Daear Consulting, LLC](https://github.com/daearconsulting)), in consultation with 
James Sanovia, MS ([Daear Consulting, LLC](https://github.com/daearconsulting)), enrolled member of the Rosebud Sioux Tribe (Sicangu Lakota Oyate). 




