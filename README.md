# Tribal Fire Science & Indigenous Data Sovereignty

> Jupyter notebooks and shared Python modules for analyzing wildfire history, risk, and stewardship on and near Tribal lands in the United States, modular code, and OCAP®-aligned data governance.

**Author:** Lilly Jones, PhD (Daear Consulting, LLC) 
**Version:** 1.0.0 · Released February 2026  
**License:** See [LICENSE](LICENSE)  
**Citation:** See [citation.cff](citation.cff) or the [cite this repo](#citation) section below

## Why This Repo Exists

Tribal nations face disproportionate wildfire risk, yet most fire science tools and datasets are built without Tribal input and applied without Tribal oversight. This project exists to change that by providing open, reproducible, and sovereignty-conscious tools for Tribal-led fire research and land management.

All analysis uses real, documented public data sources. No synthetic data. All code is modular and designed to be extended by Tribal colleges, land managers, and researchers working at the intersection of Indigenous data sovereignty and fire science.

## Notebooks

| Notebook | Description |
|---|---|
| `historical_fast_fires_tribal.ipynb` | Historical wildfire analysis (MTBS 1984–present) on and near Tribal lands (frequency, severity, and risk scores) by tribe |
| `fast_fire_days_analysis.ipynb` | Identifies and analyzes days with rapid fire growth using weather and fire occurrence data |
| `community_assets_at_risk.ipynb` | Maps Tribal community assets (infrastructure, housing, cultural sites) within fire risk zones |
| `tribal_wui_pressure_index.ipynb` | Quantifies Wildland-Urban Interface (WUI) pressure on Tribal lands using WUI and fire perimeter data |
| `tribal_fire_capacity_analysis.ipynb` | Assesses fire suppression and response capacity across Tribal nations |
| `jurisdictional_complexity_analysis.ipynb` | Analyzes overlapping federal, state, and Tribal fire jurisdictions and their management implications |
| `indigenous_fire_stewardship.ipynb` | Documents and contextualizes Indigenous prescribed fire traditions and their relationship to modern fire management |
| `funding_resource_alignment.ipynb` | Examines alignment between Tribal fire risk profiles and available federal funding and resources |
| `cross_tribal_collaboration.ipynb` | Identifies opportunities for inter-tribal fire management coordination based on shared risk and geography |

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
- File/Open Folder `tribal_fire_science`
- `Ctrl+Shift+P` **Python: Select Interpreter** `tribal-fire-science`

### 5. Run your first notebook
Open `notebooks/historical_fast_fires_tribal.ipynb` and run all cells.
The Census TIGER tribal boundaries will download and cache automatically on first run.

## Modular Data Setup

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

All cached data is stored in `data/cache/` and `data/raw/`, both are gitignored and never committed to the repo.

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
│   │   ├── loaders.py       # Fetch + cache functions for every dataset
│   │   └── validators.py    # Data integrity checks — no synthetic fallbacks
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
| Historical Fire Analysis & Risk Mapping | Understand past fire behavior to predict future risk |
| Fire Behavior Simulation | Model fire spread using FARSITE / FlamMap under varying conditions |
| Fire Impact on Cultural & Ecological Resources | Protect sacred sites, heritage areas, and ecocultural plants |
| Real-Time Fire Monitoring & Early Warning | Track active fires and generate dynamic risk alerts |
| Prescribed Burn Planning & Optimization | Support controlled burns for ecosystem restoration |
| Climate Change & Fire Regime Projection | Assess how shifting climate affects Tribal fire risk |
| Multi-Scale Decision Support Dashboard | Centralize fire data for Tribal land management decisions |

## Data Sovereignty

This project is built on OCAP® principles (**Ownership, Control, Access, and Possession**) as defined by the First Nations Information Governance Centre.

- Tribal nations own their collective data and cultural knowledge
- Federal and third-party boundaries (Census, BIA) are for analysis only and do not represent tribal self-definition of territory
- Traditional Ecological Knowledge referenced in any notebook belongs to the communities that hold it and is not treated as extractable data
- This work is intended to support — not replace — Tribal-led fire science

`src/indigenous/sovereignty.py` contains data attribution metadata, OCAP® governance helpers, and a TEK disclaimer. Call `print_data_acknowledgment()` at the top of every notebook that uses Tribal data sources.

**Reference:** [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/)

## Citation

If you use this software, please cite it as:

Jones, L., & Sanovia, J. (2026). Tribal Fire Science (Version 1.0.0).
https://github.com/daearconsulting/tribal_fire_science
https://orcid.org/0009-0003-0022-1452 · https://orcid.org/0000-0002-7127-2084

Or see [`citation.cff`](citation.cff) for machine-readable citation metadata.

## Acknowledgments

This work is advised by Tribal data sovereignty work and Indigenous communities. We gratefully acknowledge the Nations whose lands and fire histories are represented in these analyses, and whose knowledge systems inform this work far beyond what any dataset can capture.

