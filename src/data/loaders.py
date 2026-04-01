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

# ── Retry decorator for flaky public APIs ──────────────────────────────────────
_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)


# ── Internal helpers ───────────────────────────────────────────────────────────

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


# ── NIFC Fire Perimeters ───────────────────────────────────────────────────────

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


# ── MTBS Burned Area Perimeters ────────────────────────────────────────────────

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


# ── BIA Tribal Boundaries ─────────────────────────────────────────────────────

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


# ── Census TIGER — American Indian / Alaska Native Areas ──────────────────────

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


# ── Native Land Digital — Tribal Territories ──────────────────────────────────

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


# ── FEMA National Risk Index ───────────────────────────────────────────────────

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


# ── WUI — Wildland-Urban Interface ────────────────────────────────────────────

@_retry
def load_wui(force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    USDA Forest Service WUI dataset (2010 base).
    Source: https://www.fs.usda.gov/rds/archive/catalog/RDS-2015-0047-2
    NOTE: Large file (~1 GB). Consider filtering by state/bbox after loading.
    """
    def _fetch():
        # Direct ZIP download — URL may require navigating USDA RDS catalog
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


# ── NOAA Climate Data (via CDO API) ───────────────────────────────────────────

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


# ── gridMET Weather Data ───────────────────────────────────────────────────────

# gridMET variable names and their units
GRIDMET_VARIABLES = {
    "tmmx":   {"desc": "Maximum temperature",        "units_raw": "K",    "units_out": "F"},
    "rmin":   {"desc": "Minimum relative humidity",  "units_raw": "%",    "units_out": "%"},
    "vs":     {"desc": "Wind velocity at 10m",       "units_raw": "m/s",  "units_out": "mph"},
    "bi":     {"desc": "Burning Index",              "units_raw": "index","units_out": "index"},
    "erc":    {"desc": "Energy Release Component",   "units_raw": "index","units_out": "index"},
    "fm1000": {"desc": "1000-hr dead fuel moisture", "units_raw": "%",    "units_out": "%"},
}

# gridMET OPeNDAP base URL — spatial subsetting via index slicing avoids
# downloading full continental US grids (~200–500 MB per variable per year)
GRIDMET_OPENDAP_BASE = (
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/MET/{var}/{var}_{year}.nc"
)


def load_gridmet_weather(
    tribal_gdf: gpd.GeoDataFrame,
    start_year: int = 2000,
    end_year: int = 2024,
    variables: list[str] | None = None,
    name_col: str = "NAME",
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Load gridMET daily weather data for Tribal land centroids.

    Uses OPeNDAP spatial subsetting to download only the grid cells
    covering the study area — no full continental US download required.

    Source: University of Idaho gridMET
    https://www.climatologylab.org/gridmet.html
    Spatial resolution: ~4 km. Temporal coverage: 1979–present.

    Variables loaded by default
    ---------------------------
    tmmx   : Daily max temperature (K → °F)
    rmin   : Daily min relative humidity (%)
    vs     : Daily mean wind speed (m/s → mph)
    bi     : Burning Index
    erc    : Energy Release Component
    fm1000 : 1000-hr dead fuel moisture (%)

    Parameters
    ----------
    tribal_gdf   : GeoDataFrame of Tribal land boundaries (EPSG:4326)
    start_year   : First year to download (inclusive)
    end_year     : Last year to download (inclusive)
    variables    : List of gridMET variable names. Defaults to all six above.
    name_col     : Column in tribal_gdf to use as Tribal land identifier
    force_refresh: Re-download even if cache exists

    Returns
    -------
    DataFrame with columns: tribal_name, date, year, month, day_of_year,
    temp_max_f, rh_min_pct, wind_mph, burning_index, erc, fm1000
    """
    try:
        import xarray as xr
        import numpy as np
    except ImportError:
        raise ImportError(
            "xarray and numpy are required for gridMET loading. "
            "Run: conda install -n tribal-fire-science xarray numpy"
        )

    from .constants import CRS_GEOGRAPHIC

    vars_to_load = variables or list(GRIDMET_VARIABLES.keys())
    cache_name = f"gridmet_{start_year}_{end_year}_{'_'.join(sorted(vars_to_load))}"
    cached = _cache_path(cache_name, ".parquet")

    if cached.exists() and not force_refresh:
        log.info("Loading gridMET data from cache: %s", cached)
        return pd.read_parquet(cached)

    # Compute centroids for point extraction.
    # Project to Albers Equal Area first to avoid geographic CRS centroid warning,
    # then extract lon/lat back in geographic CRS.
    tribal = tribal_gdf.to_crs("EPSG:5070").copy()
    centroids = tribal.geometry.centroid.to_crs(CRS_GEOGRAPHIC)
    tribal = tribal.to_crs(CRS_GEOGRAPHIC)
    tribal["centroid_lon"] = centroids.x
    tribal["centroid_lat"] = centroids.y

    all_records = []

    for year in range(start_year, end_year + 1):
        log.info("Loading gridMET year %d ...", year)
        year_data: dict[str, xr.Dataset] = {}

        for var in vars_to_load:
            url = GRIDMET_OPENDAP_BASE.format(var=var, year=year)
            try:
                ds = xr.open_dataset(url, engine="netcdf4")
                year_data[var] = ds
            except Exception as e:
                log.warning("Could not load gridMET %s %d: %s", var, year, e)
                year_data[var] = None

        # Extract values for each Tribal land centroid
        for _, row in tribal.iterrows():
            tribal_name = row[name_col]
            lon = row["centroid_lon"]
            lat = row["centroid_lat"]

            # Build one record per day
            try:
                # Use tmmx to get date range for this year
                ref_var = next(
                    (v for v in vars_to_load if year_data.get(v) is not None), None
                )
                if ref_var is None:
                    continue

                ref_ds = year_data[ref_var]
                # gridMET lat runs N→S (descending), lon runs W→E
                times = ref_ds["day"].values

                def nearest_val(ds, variable, lat, lon):
                    """Extract nearest grid cell value time series."""
                    try:
                        da = ds[variable]
                        # Select nearest lat/lon
                        point = da.sel(
                            lat=lat, lon=lon, method="nearest"
                        )
                        return point.values
                    except Exception:
                        return np.full(len(times), np.nan)

                tmmx_vals  = nearest_val(year_data.get("tmmx"),   "air_temperature",            lat, lon) if year_data.get("tmmx")   else np.full(len(times), np.nan)
                rmin_vals  = nearest_val(year_data.get("rmin"),   "relative_humidity",           lat, lon) if year_data.get("rmin")   else np.full(len(times), np.nan)
                vs_vals    = nearest_val(year_data.get("vs"),     "wind_speed",                  lat, lon) if year_data.get("vs")     else np.full(len(times), np.nan)
                bi_vals    = nearest_val(year_data.get("bi"),     "burning_index_g",             lat, lon) if year_data.get("bi")     else np.full(len(times), np.nan)
                erc_vals   = nearest_val(year_data.get("erc"),    "energy_release_component-g",  lat, lon) if year_data.get("erc")    else np.full(len(times), np.nan)
                fm_vals    = nearest_val(year_data.get("fm1000"), "dead_fuel_moisture_1000hr",   lat, lon) if year_data.get("fm1000") else np.full(len(times), np.nan)

                # Unit conversions
                # K → °F
                temp_f = (tmmx_vals - 273.15) * 9 / 5 + 32
                # m/s → mph
                wind_mph = vs_vals * 2.23694

                dates = pd.to_datetime(times)

                for i, date in enumerate(dates):
                    all_records.append({
                        "tribal_name":    tribal_name,
                        "date":           date,
                        "year":           date.year,
                        "month":          date.month,
                        "day_of_year":    date.day_of_year,
                        "temp_max_f":     float(temp_f[i])   if not np.isnan(temp_f[i])   else np.nan,
                        "rh_min_pct":     float(rmin_vals[i])if not np.isnan(rmin_vals[i])else np.nan,
                        "wind_mph":       float(wind_mph[i]) if not np.isnan(wind_mph[i]) else np.nan,
                        "burning_index":  float(bi_vals[i])  if not np.isnan(bi_vals[i])  else np.nan,
                        "erc":            float(erc_vals[i]) if not np.isnan(erc_vals[i]) else np.nan,
                        "fm1000":         float(fm_vals[i])  if not np.isnan(fm_vals[i])  else np.nan,
                    })

            except Exception as e:
                log.warning("Error extracting gridMET for %s %d: %s", tribal_name, year, e)

        # Close datasets to free memory
        for ds in year_data.values():
            if ds is not None:
                ds.close()

    if not all_records:
        raise ValueError(
            "No gridMET records were extracted. Check network access to "
            "thredds.northwestknowledge.net and verify Tribal land coordinates."
        )

    df = pd.DataFrame(all_records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["tribal_name", "date"]).reset_index(drop=True)

    # Cache result
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    df.to_parquet(cached, index=False)
    log.info("gridMET data cached to %s", cached)

    return df


# ── HIFLD Fire Stations ────────────────────────────────────────────────────────

HIFLD_FIRE_STATIONS_URL = (
    "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/"
    "Fire_Stations/FeatureServer/0/query"
)


@_retry
def load_hifld_fire_stations(
    state_filter: list[str] | None = None,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    HIFLD Fire Stations — federal, state, local, and Tribal fire stations.
    Source: Homeland Infrastructure Foundation-Level Data (HIFLD)
    https://hifld-geoplatform.opendata.arcgis.com/datasets/fire-stations

    Parameters
    ----------
    state_filter : list of two-letter state abbreviations to filter results
                   (e.g. ["AZ", "NM", "MT"]). If None, returns all CONUS stations.
    force_refresh : re-download even if cache exists
    """
    cache_name = "hifld_fire_stations"
    if state_filter:
        cache_name += "_" + "_".join(sorted(state_filter))

    def _fetch():
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        if not state_filter:
            raise ValueError(
                "state_filter is required for load_hifld_fire_stations to avoid "
                "requesting the full national dataset. Pass a list of state "
                "abbreviations, e.g. state_filter=['AZ', 'NM']."
            )

        states = "', '".join(state_filter)
        where_clause = f"STATE IN ('{states}')"

        # Paginate — HIFLD service max is 1000 records per request
        all_features = []
        offset = 0
        page_size = 1000

        while True:
            params = {
                "where":             where_clause,
                "outFields":         "*",
                "f":                 "geojson",
                "resultRecordCount": page_size,
                "resultOffset":      offset,
                "outSR":             "4326",
            }
            r = requests.get(HIFLD_FIRE_STATIONS_URL, params=params, timeout=120)
            r.raise_for_status()
            data = r.json()
            features = data.get("features", [])
            all_features.extend(features)
            log.info("HIFLD: fetched %d records (offset %d)", len(features), offset)
            # Stop when fewer records than page_size returned
            if len(features) < page_size:
                break
            offset += page_size

        if not all_features:
            raise ValueError(
                f"No HIFLD fire stations returned for states: {state_filter}. "
                "Check state abbreviations and network access."
            )

        gdf = gpd.GeoDataFrame.from_features(all_features, crs=CRS_GEOGRAPHIC)
        gdf = gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty].copy()
        return gdf

    return _load_or_fetch_geodataframe(cache_name, _fetch, force_refresh)


# ── USGS Watershed Boundary Dataset (WBD) HUC-8 ───────────────────────────────

USGS_WBD_URL = (
    "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/4/query"
)


@_retry
def load_usgs_wbd_huc8(
    bbox: tuple[float, float, float, float] | None = None,
    huc2_codes: list[str] | None = None,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    USGS Watershed Boundary Dataset — HUC-8 subbasins.
    Source: https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/4

    Parameters
    ----------
    bbox       : (min_lon, min_lat, max_lon, max_lat) spatial filter
    huc2_codes : list of 2-digit HUC region codes (e.g. ["17", "11"])
                 to limit download. If None, uses bbox only.
    force_refresh : re-download even if cache exists
    """
    cache_name = "usgs_wbd_huc8"
    if huc2_codes:
        cache_name += "_" + "_".join(sorted(huc2_codes))
    if bbox:
        cache_name += f"_{bbox[0]:.1f}_{bbox[1]:.1f}_{bbox[2]:.1f}_{bbox[3]:.1f}"

    def _fetch():
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        # The USGS WBD endpoint returns 500 when combining WHERE and spatial filter.
        # Always use bbox-only spatial filtering; huc2_codes filtering is done
        # in Python after loading via huc8.str[:2].
        where = "1=1"

        params = {
            "where":             where,
            "outFields":         "huc8,name,areasqkm,states",
            "f":                 "geojson",
            "returnGeometry":    "true",
            "resultRecordCount": 2000,
            "outSR":             "4326",
        }

        if bbox:
            params["geometry"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
            params["geometryType"] = "esriGeometryEnvelope"
            params["spatialRel"] = "esriSpatialRelIntersects"
            params["inSR"] = "4326"

        all_features = []
        offset = 0
        while True:
            params["resultOffset"] = offset
            r = requests.get(USGS_WBD_URL, params=params, timeout=120)
            r.raise_for_status()
            features = r.json().get("features", [])
            all_features.extend(features)
            if len(features) < 2000:
                break
            offset += 2000

        if not all_features:
            raise ValueError(
                "No WBD HUC-8 watersheds returned. "
                "Check bbox or huc2_codes parameters."
            )

        gdf = gpd.GeoDataFrame.from_features(all_features, crs=CRS_GEOGRAPHIC)
        return gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty].copy()

    return _load_or_fetch_geodataframe(cache_name, _fetch, force_refresh)


# ── EPA Level III Ecoregions ───────────────────────────────────────────────────

EPA_ECOREGIONS_L3_URL = (
    "https://geodata.epa.gov/arcgis/rest/services/ORD/NATL_ECO_L3_SIMP/MapServer/0/query"
)


@_retry
def load_epa_ecoregions_l3(
    bbox: tuple[float, float, float, float] | None = None,
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    EPA Level III Ecoregions (simplified).
    Source: https://geodata.epa.gov/arcgis/rest/services/ORD/NATL_ECO_L3_SIMP/MapServer/0

    Parameters
    ----------
    bbox : (min_lon, min_lat, max_lon, max_lat) spatial filter
    """
    cache_name = "epa_ecoregions_l3"
    if bbox:
        cache_name += f"_{bbox[0]:.1f}_{bbox[1]:.1f}_{bbox[2]:.1f}_{bbox[3]:.1f}"

    def _fetch():
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        params = {
            "where":             "1=1",
            "outFields":         "US_L3CODE,US_L3NAME,NA_L2NAME,NA_L1NAME",
            "f":                 "geojson",
            "returnGeometry":    "true",
            "resultRecordCount": 500,
            "outSR":             "4326",
        }

        if bbox:
            params["geometry"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
            params["geometryType"] = "esriGeometryEnvelope"
            params["spatialRel"] = "esriSpatialRelIntersects"
            params["inSR"] = "4326"

        all_features = []
        offset = 0
        while True:
            params["resultOffset"] = offset
            r = requests.get(EPA_ECOREGIONS_L3_URL, params=params, timeout=120)
            r.raise_for_status()
            features = r.json().get("features", [])
            all_features.extend(features)
            if len(features) < 500:
                break
            offset += 500

        if not all_features:
            raise ValueError(
                "No EPA Level III ecoregions returned. Check bbox parameter."
            )

        gdf = gpd.GeoDataFrame.from_features(all_features, crs=CRS_GEOGRAPHIC)
        return gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty].copy()

    return _load_or_fetch_geodataframe(cache_name, _fetch, force_refresh)


# ── BLM Surface Management Agency (SMA) ───────────────────────────────────────

BLM_SMA_URL = (
    "https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_LimitedScale/"
    "MapServer/1/query"
)


@_retry
def load_blm_sma(
    bbox: tuple[float, float, float, float],
    force_refresh: bool = False,
) -> gpd.GeoDataFrame:
    """
    BLM Surface Management Agency (SMA) dataset — federal land ownership.
    Includes BLM, USFS, NPS, FWS, BIA, DOD, state, and private surface ownership.
    Source: https://gbp-blm-egis.hub.arcgis.com/

    Parameters
    ----------
    bbox : (min_lon, min_lat, max_lon, max_lat) — required, clips to study area
    """
    if bbox is None:
        raise ValueError("bbox is required for load_blm_sma to limit download size.")

    cache_name = f"blm_sma_{bbox[0]:.2f}_{bbox[1]:.2f}_{bbox[2]:.2f}_{bbox[3]:.2f}"

    def _fetch():
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        all_features = []
        offset = 0
        page_size = 1000

        while True:
            params = {
                "where":             "1=1",
                "outFields":         "ADMIN_AGENCY_CODE,ADMIN_UNIT_NAME,BLM_STATE_CODE",
                "f":                 "geojson",
                "returnGeometry":    "true",
                "resultRecordCount": page_size,
                "resultOffset":      offset,
                "outSR":             "4326",
                "geometry":          f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
                "geometryType":      "esriGeometryEnvelope",
                "spatialRel":        "esriSpatialRelIntersects",
                "inSR":              "4326",
            }
            r = requests.get(BLM_SMA_URL, params=params, timeout=120)
            r.raise_for_status()
            features = r.json().get("features", [])
            all_features.extend(features)
            log.info("BLM SMA: fetched %d records (offset %d)", len(features), offset)
            if len(features) < page_size:
                break
            offset += page_size

        if not all_features:
            raise ValueError(
                "No BLM SMA features returned for bbox. "
                "Check bbox coordinates and network access."
            )

        gdf = gpd.GeoDataFrame.from_features(all_features, crs=CRS_GEOGRAPHIC)
        return gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty].copy()

    return _load_or_fetch_geodataframe(cache_name, _fetch, force_refresh)


# ── Census TIGER Urban Areas ───────────────────────────────────────────────────

CENSUS_UAC_URL = f"{CENSUS_TIGER_BASE}/TIGER2023/UAC/tl_2023_us_uac20.zip"


@_retry
def load_census_urban_areas(force_refresh: bool = False) -> gpd.GeoDataFrame:
    """
    Census TIGER Urban Areas (UAC), 2020 delineation, 2023 vintage.
    Includes Urbanized Areas (>=50,000 pop) and Urban Clusters (2,500–50,000 pop).
    Source: https://www2.census.gov/geo/tiger/TIGER2023/UAC/

    Returns
    -------
    GeoDataFrame with columns: NAME20, UATYPE20 (U=Urbanized, C=Cluster), geometry
    """
    def _fetch():
        try:
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass

        log.info("Downloading Census Urban Areas from %s", CENSUS_UAC_URL)
        r = requests.get(CENSUS_UAC_URL, timeout=300)
        r.raise_for_status()
        zip_path = RAW_DIR / "tl_2023_us_uac20.zip"
        zip_path.write_bytes(r.content)
        extract_dir = RAW_DIR / "census_uac"
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(extract_dir)
        shp = next(extract_dir.glob("*.shp"))
        gdf = gpd.read_file(shp)
        return gdf.to_crs(CRS_GEOGRAPHIC)

    return _load_or_fetch_geodataframe("census_urban_areas", _fetch, force_refresh)


# ── Census ACS Population ─────────────────────────────────────────────────────

def load_census_acs_population(
    api_key: str,
    year: int = 2022,
    variables: list[str] | None = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Census American Community Survey (ACS) 5-year estimates — county population.
    Source: https://api.census.gov/data/

    Parameters
    ----------
    api_key   : Census API key (free from https://api.census.gov/data/key_signup.html)
               Store in .env as CENSUS_API_KEY, never commit.
    year      : ACS release year (e.g. 2022 = 2018-2022 5-year estimates)
    variables : List of ACS variable codes. Defaults to ['B01003_001E'] (total population).

    Returns
    -------
    DataFrame with state, county, and population columns.
    """
    vars_to_fetch = variables or ["B01003_001E"]
    cache_name = f"census_acs_{year}_{'_'.join(sorted(vars_to_fetch))}"

    def _fetch():
        try:
            from census import Census
        except ImportError:
            raise ImportError(
                "census package is required. Run: pip install census"
            )

        c   = Census(api_key, year=year)
        raw = c.acs5.get(vars_to_fetch, {"for": "county:*", "in": "state:*"})
        df  = pd.DataFrame(raw)
        # Rename population column
        if "B01003_001E" in df.columns:
            df = df.rename(columns={"B01003_001E": "total_population"})
            df["total_population"] = pd.to_numeric(df["total_population"], errors="coerce")
        return df

    return _load_or_fetch_dataframe(cache_name, _fetch, force_refresh)

