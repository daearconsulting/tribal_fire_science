"""
constants.py — Shared configuration for paths, CRS, and tribal identifiers.

All paths are relative to REPO_ROOT so the project works on any machine
or GitHub clone without modification.
"""

from pathlib import Path

# Repo layout 
REPO_ROOT   = Path(__file__).resolve().parents[2]
DATA_DIR    = REPO_ROOT / "data"
RAW_DIR     = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"     # processed but not final
FINAL_DIR   = DATA_DIR / "final"       # analysis-ready
CACHE_DIR   = DATA_DIR / "cache"       # API response cache (gitignored)
OUTPUTS_DIR = REPO_ROOT / "outputs"
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"

# Ensure directories exist at import time.
# Explicit try/except avoids a Windows pathlib edge case where exist_ok=True
# still raises FileExistsError when a parent directory already exists.
for _d in [RAW_DIR, INTERIM_DIR, FINAL_DIR, CACHE_DIR, OUTPUTS_DIR]:
    try:
        _d.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass


# Coordinate Reference Systems 
CRS_GEOGRAPHIC = "EPSG:4326"    # WGS 84 lat/lon for web maps / APIs
CRS_PROJECTED  = "EPSG:5070"    # Albers Equal Area Conus area calculations
CRS_WEB_MERCATOR = "EPSG:3857"  # Web Mercator contextily basemaps


# Data source URLs 
# National Interagency Fire Center (NIFC)
NIFC_PERIMETERS_URL = (
    "https://opendata.arcgis.com/datasets/"
    "5da472c6d27b4b67970acc7b5044c862_0.geojson"
)
NIFC_STATS_URL = "https://www.nifc.gov/fire-information/statistics/suppression-costs"

# USDA Forest Service Fire occurrence database
USFS_FIRE_OCCURRENCE_URL = (
    "https://www.fs.usda.gov/rds/archive/catalog/RDS-2013-0009"
)

# Bureau of Indian Affairs Tribal boundaries (via BIA Geospatial)
BIA_TRIBAL_BOUNDARIES_URL = (
    "https://biamaps.doi.gov/biaatlas/geoserver/DivLTR/ows?"
    "service=WFS&version=1.0.0&request=GetFeature"
    "&typeName=DivLTR:BIA_National_LAR&outputFormat=application/json"
)

# MTBS Monitoring Trends in Burn Severity
MTBS_PERIMETERS_URL = (
    "https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/MTBS_Fire/"
    "data/composite_data/burned_area_extent_shapefile/"
    "mtbs_perimeter_data.zip"
)
MTBS_BURNED_AREA_URL = "https://www.mtbs.gov/direct-download"

# US Census TIGER shapefiles
CENSUS_TIGER_BASE = "https://www2.census.gov/geo/tiger"
CENSUS_AIAN_URL   = f"{CENSUS_TIGER_BASE}/TIGER2023/AIANNH/"  # AI/AN areas

# Red Cross / FEMA Community assets (used in community_assets_at_risk)
FEMA_NFHL_URL = (
    "https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer"
)
FEMA_NATIONAL_RISK_INDEX_URL = (
    "https://hazards.fema.gov/nri/Content/StaticDocuments/DataDownload/"
    "NRI_Shapefile_States/NRI_Shapefile_States.zip"
)

# USDA Forest Service WUI (Wildland-Urban Interface)
WUI_URL = (
    "https://www.fs.usda.gov/rds/archive/catalog/RDS-2015-0047-2"
)

# NOAA Climate / Red Flag Warning days
NOAA_CLIMATE_URL  = "https://www.ncei.noaa.gov/cdo-web/api/v2/"
NOAA_RAWS_URL     = "https://raws.nifc.gov/"

# EPA Air quality (smoke / PM2.5)
EPA_AQS_URL = "https://aqs.epa.gov/data/api/"

# Native Land Digital — Tribal territory polygons
NATIVE_LAND_API = "https://native-land.ca/api/index.php"


# Federal Indian Regions
# BIA Regional Office codes human-readable names
BIA_REGIONS = {
    "AK": "Alaska",
    "EA": "Eastern",
    "ES": "Eastern Oklahoma",
    "GP": "Great Plains",
    "MP": "Midwest",
    "MT": "Midwest (Minnesota)",  # sometimes split
    "NA": "Navajo",
    "NW": "Northwest",
    "PA": "Pacific",
    "RM": "Rocky Mountain",
    "SO": "Southern Plains",
    "SW": "Southwest",
    "WS": "Western",
}

# Wildfire risk / behavior thresholds 
# Fast-fire definition: >10,000 acres in first operational period (source: NIFC)
FAST_FIRE_ACRES_THRESHOLD = 10_000

# Red flag wind speed threshold (mph) used in fast_fire_days_analysis
RED_FLAG_WIND_MPH = 25

# Visualization defaults 
DEFAULT_MAP_CENTER  = [39.5, -98.35]   # geographic center of contiguous US
DEFAULT_MAP_ZOOM    = 4
TRIBAL_ACCENT_COLOR = "#C8522B"        # terra cotta