# `/src` — Shared Module Reference

Utilities shared across all notebooks in the Tribal Fire Science & Indigenous Data Sovereignty series.

## Structure

```
src/
├── __init__.py              # Exposes REPO_ROOT
├── data/
│   ├── constants.py         # Paths, CRS, URLs, thresholds
│   ├── loaders.py           # Fetch + cache functions for every dataset
│   └── validators.py        # Integrity checks — no synthetic data fallbacks
├── viz/
│   ├── styles.py            # Color palettes, design tokens, mpl rcParams
│   ├── maps.py              # Folium base maps, tribal boundary layers, choropleths
│   └── charts.py            # Timeline bars, heatmaps, capacity bars, scatter plots
├── geo/
│   └── utils.py             # CRS helpers, spatial joins, area calculations
└── indigenous/
    └── sovereignty.py       # OCAP® data governance, attribution, TEK disclaimer
```

## Importing in Notebooks

```python
import sys
from pathlib import Path

REPO_ROOT = Path().resolve().parents[0]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data import constants, loaders, validators
from src.viz import maps, charts, styles
from src.geo import utils as geo_utils
from src.indigenous.sovereignty import print_data_acknowledgment
```

## Data Sovereignty

All tribal datasets are flagged in `sovereignty.py`. Call `print_data_acknowledgment()` at the top of every notebook that uses tribal data sources. See OCAP® principles: https://fnigc.ca/ocap-training/

## Data Sources

All data is fetched from real public sources. No synthetic data. Sources are cached locally in `data/cache/` (gitignored). Pass `force_refresh=True` to any loader to re-download.

| Source | Loader | Notes |
|---|---|---|
| NIFC Fire Perimeters | `loaders.load_nifc_perimeters()` | Current year |
| MTBS Burned Areas | `loaders.load_mtbs_perimeters()` | 1984–present |
| BIA Tribal Boundaries | `loaders.load_bia_tribal_boundaries()` | Federal LAR |
| Census TIGER AIANNH | `loaders.load_census_aian()` | 2023 vintage |
| Native Land Digital | `loaders.load_native_land_territories()` | CC BY-NC 4.0 |
| FEMA National Risk Index | `loaders.load_fema_national_risk_index()` | County level |
| WUI Dataset | `loaders.load_wui()` | Manual download required |
| NOAA Climate Data | `loaders.load_noaa_climate_data()` | API token required |
