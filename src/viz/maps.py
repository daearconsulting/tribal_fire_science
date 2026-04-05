"""
maps.py: reusable folium map helpers for tribal fire science notebooks.
"""

from __future__ import annotations

from typing import Optional

import folium
import geopandas as gpd
from folium.plugins import Fullscreen, MiniMap

from ..data.constants import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM
from .styles import (
    FIRE_PERIMETER_STYLE,
    TRIBAL_BOUNDARY_STYLE,
    CHOROPLETH_DEFAULTS,
    FIRE_RISK_RAMP,
)


def base_map(
    center: list[float] = DEFAULT_MAP_CENTER,
    zoom: int = DEFAULT_MAP_ZOOM,
    tiles: str = "CartoDB positron",
    minimap: bool = True,
    fullscreen: bool = True,
) -> folium.Map:
    """
    Create a standard base map with optional minimap and fullscreen controls.

    Parameters
    center    : [lat, lon]
    zoom      : initial zoom level
    tiles     : folium tile provider string
    minimap   : add a minimap overview
    fullscreen: add a fullscreen button
    """
    m = folium.Map(location=center, zoom_start=zoom, tiles=tiles)
    if minimap:
        MiniMap(toggle_display=True).add_to(m)
    if fullscreen:
        Fullscreen(position="topright").add_to(m)
    return m


def add_tribal_boundaries(
    m: folium.Map,
    gdf: gpd.GeoDataFrame,
    name: str = "Tribal Boundaries",
    tooltip_field: Optional[str] = None,
    style: Optional[dict] = None,
) -> folium.Map:
    """
    Add Tribal boundary polygons as a named layer.
    Parameters
    tooltip_field : column name to show on hover (ex. "NAMELSAD")
    """
    layer_style = style or TRIBAL_BOUNDARY_STYLE

    layer = folium.FeatureGroup(name=name, show=True)
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        tooltip = str(row[tooltip_field]) if tooltip_field and tooltip_field in row else None
        folium.GeoJson(
            geom.__geo_interface__,
            style_function=lambda _: layer_style,
            tooltip=tooltip,
        ).add_to(layer)
    layer.add_to(m)
    return m


def add_fire_perimeters(
    m: folium.Map,
    gdf: gpd.GeoDataFrame,
    name: str = "Fire Perimeters",
    tooltip_fields: Optional[list[str]] = None,
    style: Optional[dict] = None,
) -> folium.Map:
    """
    Add fire perimeter polygons as a named, toggleable layer.
    Parameters
    tooltip_fields : columns to include in tooltip (ex. ["IncidentName", "GISAcres"])
    """
    layer_style = style or FIRE_PERIMETER_STYLE
    layer = folium.FeatureGroup(name=name, show=True)

    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        if tooltip_fields:
            tip_html = "<br>".join(
                f"<b>{f}:</b> {row[f]}" for f in tooltip_fields if f in row
            )
        else:
            tip_html = None
        folium.GeoJson(
            geom.__geo_interface__,
            style_function=lambda _: layer_style,
            tooltip=folium.Tooltip(tip_html) if tip_html else None,
        ).add_to(layer)
    layer.add_to(m)
    return m


def add_choropleth(
    m: folium.Map,
    gdf: gpd.GeoDataFrame,
    value_column: str,
    key_column: str,
    name: str = "Choropleth",
    legend_name: str = "",
    color_ramp: list[str] = FIRE_RISK_RAMP,
    bins: int = 5,
) -> folium.Map:
    """
    Add a choropleth layer from a GeoDataFrame column.
    """
    import json

    geo_json_data = json.loads(gdf.to_json())

    folium.Choropleth(
        geo_data=geo_json_data,
        name=name,
        data=gdf,
        columns=[key_column, value_column],
        key_on=f"feature.properties.{key_column}",
        fill_color="YlOrRd",
        fill_opacity=CHOROPLETH_DEFAULTS["fill_opacity"],
        line_opacity=CHOROPLETH_DEFAULTS["line_opacity"],
        line_weight=CHOROPLETH_DEFAULTS["line_weight"],
        legend_name=legend_name or value_column,
        bins=bins,
    ).add_to(m)

    return m


def save_map(m: folium.Map, path: str) -> None:
    """Save map to an HTML file (relative path from repo root)."""
    from pathlib import Path
    from src import REPO_ROOT
    out = REPO_ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(out))
    print(f"Map saved → {out}")
