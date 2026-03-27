"""
geo/utils.py: CRS management, spatial joins, and geometry helpers.
"""

from __future__ import annotations

import logging
from typing import Optional

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from ..data.constants import CRS_GEOGRAPHIC, CRS_PROJECTED

log = logging.getLogger(__name__)


# CRS helpers 

def to_geographic(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject to WGS 84 geographic (EPSG:4326)."""
    if gdf.crs is None:
        raise ValueError("GeoDataFrame has no CRS set — cannot reproject.")
    return gdf.to_crs(CRS_GEOGRAPHIC)


def to_projected(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Reproject to Albers Equal Area (EPSG:5070) for area calculations."""
    if gdf.crs is None:
        raise ValueError("GeoDataFrame has no CRS set — cannot reproject.")
    return gdf.to_crs(CRS_PROJECTED)


def ensure_crs(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:
    """Reproject only if not already in target CRS."""
    if gdf.crs is None or str(gdf.crs) != target_crs:
        return gdf.to_crs(target_crs)
    return gdf


# Area calculation 

def add_area_acres(
    gdf: gpd.GeoDataFrame,
    col_name: str = "calc_acres",
) -> gpd.GeoDataFrame:
    """
    Add a calculated area column (acres) using Albers Equal Area projection.
    Original CRS is restored after calculation.
    """
    original_crs = gdf.crs
    projected = to_projected(gdf)
    gdf = gdf.copy()
    # 1 sq meter = 0.000247105 acres
    gdf[col_name] = projected.geometry.area * 0.000247105
    return ensure_crs(gdf, str(original_crs))


# Bounding box 

def bbox_from_gdf(gdf: gpd.GeoDataFrame, buffer_deg: float = 0.0) -> tuple:
    """
    Return (min_lon, min_lat, max_lon, max_lat) from a GeoDataFrame's total bounds.
    Optionally buffer in degrees (only meaningful for geographic CRS).
    """
    minx, miny, maxx, maxy = gdf.total_bounds
    return (minx - buffer_deg, miny - buffer_deg, maxx + buffer_deg, maxy + buffer_deg)


def bbox_geodataframe(bounds: tuple[float, float, float, float], crs: str = CRS_GEOGRAPHIC) -> gpd.GeoDataFrame:
    """Create a single-row GeoDataFrame from a bounding box tuple."""
    return gpd.GeoDataFrame(geometry=[box(*bounds)], crs=crs)


# Spatial join helpers 

def fires_within_tribal_lands(
    fires_gdf: gpd.GeoDataFrame,
    tribal_gdf: gpd.GeoDataFrame,
    how: str = "inner",
    predicate: str = "intersects",
) -> gpd.GeoDataFrame:
    """
    Spatial join of fire perimeters to tribal land boundaries.
    Returns fires with tribal attributes attached.

    Parameters
    ----------
    how       : 'inner' (fires that intersect tribal land only) or 'left'
    predicate : 'intersects', 'within', 'contains'
    """
    fires = ensure_crs(fires_gdf, CRS_GEOGRAPHIC)
    tribal = ensure_crs(tribal_gdf, CRS_GEOGRAPHIC)

    joined = gpd.sjoin(fires, tribal, how=how, predicate=predicate)
    log.info(
        "Spatial join: %d fires → %d intersecting tribal lands.",
        len(fires), len(joined),
    )
    return joined


def overlap_area_fraction(
    gdf_a: gpd.GeoDataFrame,
    gdf_b: gpd.GeoDataFrame,
) -> pd.Series:
    """
    For each feature in gdf_a, return the fraction of its area overlapping gdf_b.
    Uses Albers Equal Area for accurate area measurement.
    """
    a = to_projected(ensure_crs(gdf_a, CRS_GEOGRAPHIC)).copy()
    b = to_projected(ensure_crs(gdf_b, CRS_GEOGRAPHIC)).copy()

    b_union = b.union_all()

    fractions = []
    for geom in a.geometry:
        if geom is None or geom.is_empty:
            fractions.append(0.0)
            continue
        intersection = geom.intersection(b_union)
        frac = intersection.area / geom.area if geom.area > 0 else 0.0
        fractions.append(frac)

    return pd.Series(fractions, index=a.index, name="overlap_fraction")


# Tribal land coverage 

def summarize_fire_tribal_overlap(
    fires_gdf: gpd.GeoDataFrame,
    tribal_gdf: gpd.GeoDataFrame,
    tribal_name_col: str = "NAMELSAD",
    fire_name_col: str = "IncidentName",
    fire_acres_col: str = "GISAcres",
) -> pd.DataFrame:
    """
    Produce a summary DataFrame of fire acres within each tribal land unit.
    """
    fires = ensure_crs(fires_gdf, CRS_GEOGRAPHIC)
    tribal = ensure_crs(tribal_gdf, CRS_GEOGRAPHIC)

    joined = gpd.sjoin(fires, tribal[[tribal_name_col, "geometry"]], how="left", predicate="intersects")

    summary = (
        joined.groupby(tribal_name_col)[fire_acres_col]
        .agg(fire_count="count", total_acres="sum", mean_acres="mean")
        .reset_index()
        .sort_values("total_acres", ascending=False)
    )
    return summary
