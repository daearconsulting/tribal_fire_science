"""
validators.py — Data integrity checks for all loaded datasets.

Philosophy: If data is missing or malformed, raise — never substitute
synthetic data. Notebooks should be explicit about data provenance.
"""

from __future__ import annotations

import logging
from typing import Sequence

import geopandas as gpd
import pandas as pd

log = logging.getLogger(__name__)

# ── Required column sets by dataset ───────────────────────────────────────────
REQUIRED_COLUMNS = {
    "nifc_perimeters": ["geometry", "IncidentName", "GISAcres"],
    "mtbs_perimeters": ["geometry", "Ig_Date", "BurnBndAc", "Incid_Name"],
    "bia_tribal_boundaries": ["geometry"],
    "census_aiannh": ["geometry", "NAMELSAD", "AIANNHCE"],
    "fema_nri": ["geometry", "STATEABBRV", "RISK_SCORE"],
}


def validate_geodataframe(
    gdf: gpd.GeoDataFrame,
    dataset_name: str,
    min_rows: int = 1,
    required_columns: Sequence[str] | None = None,
    expected_crs: str | None = None,
) -> gpd.GeoDataFrame:
    """
    Run standard checks on a GeoDataFrame.

    Raises
    ------
    ValueError  : if shape, columns, or CRS don't meet expectations
    """
    if gdf is None or len(gdf) == 0:
        raise ValueError(f"[{dataset_name}] Dataset is empty.")

    if len(gdf) < min_rows:
        raise ValueError(
            f"[{dataset_name}] Expected >= {min_rows} rows, got {len(gdf)}."
        )

    # Geometry presence
    if "geometry" not in gdf.columns or gdf.geometry.isnull().all():
        raise ValueError(f"[{dataset_name}] No valid geometries found.")

    null_geom = gdf.geometry.isnull().sum()
    if null_geom > 0:
        log.warning("[%s] %d rows have null geometry — dropping.", dataset_name, null_geom)
        gdf = gdf[gdf.geometry.notnull()].copy()

    # Column check
    cols = required_columns or REQUIRED_COLUMNS.get(dataset_name, [])
    missing = [c for c in cols if c not in gdf.columns]
    if missing:
        raise ValueError(
            f"[{dataset_name}] Missing required columns: {missing}. "
            f"Available: {list(gdf.columns)}"
        )

    # CRS check
    if expected_crs and gdf.crs is not None:
        if str(gdf.crs) != expected_crs and gdf.crs.to_epsg() != int(expected_crs.split(":")[-1]):
            raise ValueError(
                f"[{dataset_name}] Expected CRS {expected_crs}, got {gdf.crs}."
            )

    log.info("[%s] Validation passed (%d rows).", dataset_name, len(gdf))
    return gdf


def validate_dataframe(
    df: pd.DataFrame,
    dataset_name: str,
    min_rows: int = 1,
    required_columns: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Run standard checks on a plain DataFrame."""
    if df is None or len(df) == 0:
        raise ValueError(f"[{dataset_name}] Dataset is empty.")

    if len(df) < min_rows:
        raise ValueError(
            f"[{dataset_name}] Expected >= {min_rows} rows, got {len(df)}."
        )

    missing = [c for c in (required_columns or []) if c not in df.columns]
    if missing:
        raise ValueError(
            f"[{dataset_name}] Missing required columns: {missing}."
        )

    log.info("[%s] Validation passed (%d rows).", dataset_name, len(df))
    return df


def assert_no_synthetic_data(df: pd.DataFrame | gpd.GeoDataFrame, dataset_name: str) -> None:
    """
    Raise if the dataframe appears to contain synthetic/placeholder data.
    Checks for common synthetic data markers.
    """
    synthetic_markers = ["SYNTHETIC", "FAKE", "PLACEHOLDER", "TODO", "DUMMY", "TEST_DATA"]
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna().astype(str).str.upper()
        for marker in synthetic_markers:
            if sample.str.contains(marker).any():
                raise ValueError(
                    f"[{dataset_name}] Column '{col}' contains synthetic marker '{marker}'. "
                    "This project uses real data sources only."
                )
