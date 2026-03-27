"""
src — Tribal Fire Science & Indigenous Data Sovereignty
Shared utilities for data loading, visualization, and geospatial analysis.

Submodules
----------
data        : Dataset loaders and validators (NIFC, BIA, MTBS, Census, etc.)
viz         : Reusable map and chart helpers
geo         : CRS utilities, spatial joins, geometry helpers
indigenous  : Data governance, sovereignty, and attribution helpers (OCAP-aligned)
"""

from pathlib import Path

# Repo root is one level above this file
REPO_ROOT = Path(__file__).resolve().parent.parent

__all__ = ["REPO_ROOT"]
