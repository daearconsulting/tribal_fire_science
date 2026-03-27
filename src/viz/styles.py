"""
styles.py — Color palettes and design tokens for Tribal Fire Science notebooks.

Palette philosophy
------------------
Earth/fire tones drawn from landscape — not generic "fire red" stock palettes.
High contrast for accessibility. Avoids color combinations that carry
unintended cultural associations.
"""

from __future__ import annotations

# ── Primary palette ────────────────────────────────────────────────────────────
FIRE_ORANGE   = "#E8622A"   # active fire / high risk
EMBER_RED     = "#C0392B"   # burned / severe
SMOKE_GRAY    = "#7F8C8D"   # smoke / suppressed
ASH_WHITE     = "#ECF0F1"   # ash / low risk background
EARTH_BROWN   = "#6D4C41"   # land / tribal boundary
SKY_BLUE      = "#2980B9"   # water / cool
SAGE_GREEN    = "#7D9B5E"   # unburned vegetation / managed land
CHARCOAL      = "#2C2C2C"   # text / outlines

# ── Sequential ramp — fire risk (low → high) ──────────────────────────────────
FIRE_RISK_RAMP = [
    "#FFFFCC",  # very low
    "#FECC5C",  # low
    "#FD8D3C",  # moderate
    "#F03B20",  # high
    "#BD0026",  # very high / extreme
]

# ── Diverging ramp — change over time ─────────────────────────────────────────
DIVERGING_BLUE_RED = [
    "#2166AC",  # strong decrease
    "#92C5DE",
    "#F7F7F7",  # no change
    "#F4A582",
    "#D6604D",  # strong increase
]

# ── Categorical — tribal regions (BIA 13 regions) ────────────────────────────
# Distinct, accessible colors for up to 13 categories
TRIBAL_REGION_COLORS = [
    "#E8622A", "#2980B9", "#27AE60", "#8E44AD", "#F39C12",
    "#16A085", "#C0392B", "#2C3E50", "#7D9B5E", "#D35400",
    "#1ABC9C", "#884EA0", "#CA6F1E",
]

# ── Folium / choropleth settings ──────────────────────────────────────────────
CHOROPLETH_DEFAULTS = {
    "fill_opacity": 0.7,
    "line_opacity": 0.4,
    "line_weight": 0.5,
}

TRIBAL_BOUNDARY_STYLE = {
    "fillColor": "none",
    "color": EARTH_BROWN,
    "weight": 2.0,
    "opacity": 0.9,
    "fillOpacity": 0.0,
}

FIRE_PERIMETER_STYLE = {
    "fillColor": FIRE_ORANGE,
    "color": EMBER_RED,
    "weight": 1.5,
    "opacity": 0.9,
    "fillOpacity": 0.45,
}

# ── Matplotlib rcParams ────────────────────────────────────────────────────────
MPL_STYLE = {
    "figure.facecolor": "white",
    "axes.facecolor": "#F8F8F8",
    "axes.edgecolor": CHARCOAL,
    "axes.labelcolor": CHARCOAL,
    "xtick.color": CHARCOAL,
    "ytick.color": CHARCOAL,
    "text.color": CHARCOAL,
    "grid.color": "#DDDDDD",
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
}


def apply_mpl_style() -> None:
    """Apply project-wide matplotlib style."""
    import matplotlib as mpl
    mpl.rcParams.update(MPL_STYLE)
