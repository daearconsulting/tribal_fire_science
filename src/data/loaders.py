"""
loaders.py — Fetch and cache real datasets used across notebooks.

Design principles
-----------------
- Every function fetches from a documented public source (no synthetic data).
- Results are cached to data/cache/ as Parquet or GeoJSON to avoid redundant
  API calls. Pass force_refresh=True to re-download.
- All returned GeoDataFrames use CRS_GEOGRAPHIC (EPSG:4326) by default.
- Functions raise clear errors if a source is unreachable rather than
  silently returning empty or fake data.
"""

from __future__ import annotations

import json
import logging
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .constants import (
    BIA_TRIBAL_BOUNDARIES_URL,
    CACHE_DIR,
    CENSUS_AIAN_URL,
    CRS_GEOGRAPHIC,
    FEMA_NATIONAL_RISK_INDEX_URL,
    MTBS_PERIMETERS_URL,
    NATIVE_LAND_API,
    NIFC_PERIMETERS_URL,
    RAW_DIR,
    WUI_URL,
)

log = logging.getLogger(__name__)

# Retry decorator for public APIs 
_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)


# Internal helpers 

def _cache_path(name: str, suffix: str = ".parquet") -> Path:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    return CACHE_DIR / f"{name}{suffix}"


def _load_or_fetch_geodataframe(
    cache_name: str,
    fetch_fn,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """Return cached GeoDataFrame, or call fetch_fn() and cache the result."""
    path = _cache_path(cache_name, ".geojson")
    if path.exists() and not force_refresh:
        log.info("Loading %s from cache.", cache_name)
        return gpd.read_file(path)
    log.info("Fetching %s from source.", cache_name)
    gdf = fetch_fn()
    gdf.to_file(path, driver="GeoJSON")
    return gdf


def _load_or_fetch_dataframe(
    cache_name: str,
    fetch_fn,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Return cached DataFrame, or call fetch_fn() and cache as Parquet."""
    path = _cache_path(cache_name, ".parquet")
    if path.exists() and not force_refresh:
        log.info("Loading %s from cache.", cache_name)
        return pd.read_parquet(path)
    log.info("Fetching %s from source.", cache_name)
    df = fetch_fn()
    df.to_parquet(path, index=False)
    return df


# NIFC Fire Perimeters

@_retry
def load_nifc_perimeters(force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    NIFC current-year fire perimeters (GeoJSON).
    Source: https://data-nifc.opendata.arcgis.com
    """
    def _fetch():
        r = requests.get(NIFC_PERIMETERS_URL, timeout=60)
        r.raise_for_status()
        gdf = gpd.read_file(BytesIO(r.content))
        return gdf.to_crs(CRS_GEOGRAPHIC)

    return _load_or_fetch_geodataframe("nifc_perimeters", _fetch, force_refresh)


# MTBS Burned Area Perimeters 

@_retry
def load_mtbs_perimeters(
    start_year: int = 1984,
    end_year: Optional[int] = None,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    MTBS burned area perimeters (1984–present).
    Source: https://www.mtbs.gov
    Filters to [start_year, end_year] after loading.
    """
    def _fetch():
        r = requests.get(MTBS_PERIMETERS_URL, timeout=120, stream=True)
        r.raise_for_status()
        zip_path = RAW_DIR / "mtbs_perimeters.zip"
        zip_path.write_bytes(r.content)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(RAW_DIR / "mtbs_perimeters")
        shp = next((RAW_DIR / "mtbs_perimeters").glob("*.shp"))
        gdf = gpd.read_file(shp)
        return gdf.to_crs(CRS_GEOGRAPHIC)

    gdf = _load_or_fetch_geodataframe("mtbs_perimeters", _fetch, force_refresh)

    # Filter by year if Ig_Date column present
    if "Ig_Date" in gdf.columns:
        gdf["Ig_Date"] = pd.to_datetime(gdf["Ig_Date"], errors="coerce")
        gdf = gdf[gdf["Ig_Date"].dt.year >= start_year]
        if end_year:
            gdf = gdf[gdf["Ig_Date"].dt.year <= end_year]

    return gdf.reset_index(drop=True)


# BIA Tribal Boundaries 

@_retry
def load_bia_tribal_boundaries(force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    BIA land area representations (tribal boundaries).
    Source: BIA Geospatial — https://biamaps.doi.gov
    """
    def _fetch():
        r = requests.get(BIA_TRIBAL_BOUNDARIES_URL, timeout=60)
        r.raise_for_status()
        gdf = gpd.GeoDataFrame.from_features(
            r.json()["features"], crs=CRS_GEOGRAPHIC
        )
        return gdf

    return _load_or_fetch_geodataframe("bia_tribal_boundaries", _fetch, force_refresh)


# Census TIGER American Indian / Alaska Native Areas 

@_retry
def load_census_aian(force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    Census TIGER/Line AIANNH shapefiles (American Indian / Alaska Native /
    Native Hawaiian areas), 2023 vintage.
    Source: https://www2.census.gov/geo/tiger/TIGER2023/AIANNH/
    """
    def _fetch():
        # Ensure directories exist before writing (safe on Windows)
        for _mkdir_path in [RAW_DIR, CACHE_DIR, RAW_DIR / "census_aiannh"]:
            try:
                _mkdir_path.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                pass
        extract_dir = RAW_DIR / "census_aiannh"

        national_url = f"{CENSUS_AIAN_URL}tl_2023_us_aiannh.zip"
        log.info("Downloading Census TIGER AIANNH from %s", national_url)
        r = requests.get(national_url, timeout=120)
        r.raise_for_status()

        zip_path = RAW_DIR / "tl_2023_us_aiannh.zip"
        zip_path.write_bytes(r.content)

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(extract_dir)

        shp_files = list(extract_dir.glob("*.shp"))
        if not shp_files:
            raise FileNotFoundError(
                f"No shapefile found after extracting Census AIANNH zip to {extract_dir}"
            )
        gdf = gpd.read_file(shp_files[0])
        return gdf.to_crs(CRS_GEOGRAPHIC)

    return _load_or_fetch_geodataframe("census_aiannh", _fetch, force_refresh)


# Native Land Digital: Tribal Territories 

@_retry
def load_native_land_territories(
    bbox: Optional[tuple[float, float, float, float]] = None,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    Native Land Digital — Indigenous territory polygons.
    Source: https://native-land.ca  (CC BY-NC 4.0)
    bbox: (min_lon, min_lat, max_lon, max_lat) to spatially filter results.

    NOTE: Review Native Land Digital terms before public redistribution.
    """
    cache_name = "native_land_territories"
    if bbox:
        cache_name += f"_{bbox[0]:.2f}_{bbox[1]:.2f}_{bbox[2]:.2f}_{bbox[3]:.2f}"

    def _fetch():
        params = {"maps": "territories"}
        if bbox:
            params["bbox"] = ",".join(str(c) for c in bbox)
        r = requests.get(NATIVE_LAND_API, params=params, timeout=60)
        r.raise_for_status()
        gdf = gpd.GeoDataFrame.from_features(
            r.json()["features"], crs=CRS_GEOGRAPHIC
        )
        return gdf

    return _load_or_fetch_geodataframe(cache_name, _fetch, force_refresh)


# FEMA National Risk Index 

@_retry
def load_fema_national_risk_index(force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    FEMA National Risk Index — county-level composite risk scores.
    Source: https://hazards.fema.gov/nri/
    """
    def _fetch():
        r = requests.get(FEMA_NATIONAL_RISK_INDEX_URL, timeout=180, stream=True)
        r.raise_for_status()
        zip_path = RAW_DIR / "fema_nri_states.zip"
        zip_path.write_bytes(r.content)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(RAW_DIR / "fema_nri")
        shp = next((RAW_DIR / "fema_nri").glob("*.shp"))
        gdf = gpd.read_file(shp)
        return gdf.to_crs(CRS_GEOGRAPHIC)

    return _load_or_fetch_geodataframe("fema_nri", _fetch, force_refresh)


# Wildland-Urban Interface (WUI)

@_retry
def load_wui(force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    USDA Forest Service WUI dataset (2010 base).
    Source: https://www.fs.usda.gov/rds/archive/catalog/RDS-2015-0047-2
    NOTE: Large file (~1 GB). Consider filtering by state/bbox after loading.
    """
    def _fetch():
        # Direct ZIP download: URL may require navigating USDA RDS catalog
        # Users may need to manually download and place in data/raw/wui/
        wui_dir = RAW_DIR / "wui"
        shp_files = list(wui_dir.glob("*.shp"))
        if not shp_files:
            raise FileNotFoundError(
                "WUI shapefile not found in data/raw/wui/. "
                f"Please download from {WUI_URL} and extract there."
            )
        gdf = gpd.read_file(shp_files[0])
        return gdf.to_crs(CRS_GEOGRAPHIC)

    return _load_or_fetch_geodataframe("wui", _fetch, force_refresh)


# NOAA Climate Data (via CDO API) 

def load_noaa_climate_data(
    station_ids: list[str],
    dataset_id: str,
    start_date: str,
    end_date: str,
    api_token: str,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    NOAA Climate Data Online (CDO) API.
    Source: https://www.ncei.noaa.gov/cdo-web/api/v2/
    Requires a free API token from: https://www.ncei.noaa.gov/cdo-web/token

    Parameters
    ----------
    station_ids : list of NOAA station IDs (e.g. ["GHCND:USC00123456"])
    dataset_id  : CDO dataset (e.g. "GHCND", "NORMAL_DLY")
    start_date  : "YYYY-MM-DD"
    end_date    : "YYYY-MM-DD"
    api_token   : CDO API token (store in .env, never commit)
    """
    from .constants import NOAA_CLIMATE_URL

    cache_name = f"noaa_{dataset_id}_{start_date}_{end_date}"

    def _fetch():
        headers = {"token": api_token}
        params = {
            "datasetid": dataset_id,
            "stationid": station_ids,
            "startdate": start_date,
            "enddate": end_date,
            "limit": 1000,
            "units": "standard",
        }
        r = requests.get(
            f"{NOAA_CLIMATE_URL}data", headers=headers, params=params, timeout=60
        )
        r.raise_for_status()
        return pd.DataFrame(r.json().get("results", []))

    return _load_or_fetch_dataframe(cache_name, _fetch, force_refresh)