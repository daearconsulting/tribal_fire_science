"""
charts.py Reusable chart helpers for Tribal fire science notebooks.
"""

from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

from .styles import FIRE_RISK_RAMP, FIRE_ORANGE, EMBER_RED, apply_mpl_style

apply_mpl_style()


def fire_timeline(
    df: pd.DataFrame,
    year_col: str,
    value_col: str,
    title: str = "Fire Activity Over Time",
    ylabel: str = "Acres Burned",
    color: str = FIRE_ORANGE,
    highlight_years: Optional[Sequence[int]] = None,
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """
    Bar chart of annual fire activity with optional year highlights.

    Parameters
    highlight_years : list of years to color differently (ex. extreme fire years)
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 5))

    colors = [
        EMBER_RED if (highlight_years and y in highlight_years) else color
        for y in df[year_col]
    ]
    ax.bar(df[year_col], df[value_col], color=colors, width=0.8)
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_xlim(df[year_col].min() - 0.5, df[year_col].max() + 0.5)
    sns.despine(ax=ax)
    return ax


def risk_heatmap(
    df: pd.DataFrame,
    index_col: str,
    columns_col: str,
    values_col: str,
    title: str = "Risk Heatmap",
    figsize: tuple = (14, 8),
    cmap: str = "YlOrRd",
) -> plt.Axes:
    """
    Pivot and render a heatmap (Tribe risk category).
    """
    pivot = df.pivot(index=index_col, columns=columns_col, values=values_col)
    _, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        pivot,
        cmap=cmap,
        linewidths=0.4,
        linecolor="#CCCCCC",
        annot=True,
        fmt=".1f",
        ax=ax,
    )
    ax.set_title(title)
    return ax


def capacity_bar(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str = "Tribal Fire Capacity",
    xlabel: str = "Score",
    color: str = FIRE_ORANGE,
    figsize: tuple = (10, 6),
) -> plt.Axes:
    """
    Horizontal bar chart, good for Tribe-by-Tribe comparisons.
    """
    df_sorted = df.sort_values(value_col, ascending=True)
    _, ax = plt.subplots(figsize=figsize)
    ax.barh(df_sorted[label_col], df_sorted[value_col], color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    sns.despine(ax=ax)
    return ax


def fast_fire_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: Optional[str] = None,
    color_col: Optional[str] = None,
    title: str = "Fast Fire Events",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple = (10, 7),
) -> plt.Axes:
    """
    Scatter plot for fast-fire events.

    Parameters
    ----------
    size_col  : column to scale marker size (e.g. total acres)
    color_col : column for marker color intensity (e.g. spread rate)
    """
    _, ax = plt.subplots(figsize=figsize)

    sizes = df[size_col] / df[size_col].max() * 400 if size_col else 60
    colors = df[color_col] if color_col else FIRE_ORANGE

    scatter = ax.scatter(
        df[x_col], df[y_col],
        s=sizes,
        c=colors,
        cmap="YlOrRd" if color_col else None,
        alpha=0.75,
        edgecolors=EMBER_RED,
        linewidths=0.5,
    )
    if color_col:
        plt.colorbar(scatter, ax=ax, label=color_col)
    ax.set_title(title)
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel or y_col)
    sns.despine(ax=ax)
    return ax


def save_figure(fig: plt.Figure, path: str, dpi: int = 150) -> None:
    """Save a figure relative to REPO_ROOT."""
    from pathlib import Path
    from src import REPO_ROOT
    out = REPO_ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    print(f"Figure saved {out}")
