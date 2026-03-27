"""
sovereignty.py — Data governance, attribution, and sovereignty helpers.

This module exists because Indigenous data sovereignty principles should not be
scattered across notebooks as comments. They belong in shared, versioned code.

OCAP® Principles (First Nations Information Governance Centre):
  Ownership   — Tribal nations own their collective data and cultural knowledge
  Control     — Nations control how data is used, interpreted, and shared
  Access      — Nations have the right to access data about their communities
  Possession  — Nations should physically hold or steward data about themselves

References
----------
- FNIGC OCAP®: https://fnigc.ca/ocap-training/
- UNDRIP Article 31: https://www.un.org/development/desa/indigenouspeoples/
- US Indigenous Data Sovereignty Network: https://usindigenousdata.org
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import warnings


# Data source registry

@dataclass
class DataSource:
    """
    Metadata for a dataset used in this project.

    Parameters
    ----------
    name            : Human-readable name
    url             : Authoritative source URL
    steward         : Organization responsible for the data
    tribal_data     : True if the dataset contains Indigenous/tribal attributes
    license         : License or terms of use
    ocap_notes      : How this dataset relates to OCAP® principles
    attribution     : Required attribution string for publication
    use_restrictions: Any restrictions on how data may be used
    """
    name: str
    url: str
    steward: str
    tribal_data: bool = False
    license: str = ""
    ocap_notes: str = ""
    attribution: str = ""
    use_restrictions: str = ""

    def warn_if_restricted(self) -> None:
        if self.use_restrictions:
            warnings.warn(
                f"[{self.name}] Use restriction: {self.use_restrictions}",
                UserWarning,
                stacklevel=2,
            )

    def citation(self) -> str:
        """Return formatted citation string."""
        return f"{self.name}. {self.steward}. {self.url}"


# Canonical dataset registry 
# These mirror the sources in data/loaders.py. Update both when adding sources.

SOURCES: dict[str, DataSource] = {
    "nifc_perimeters": DataSource(
        name="NIFC Current Year Fire Perimeters",
        url="https://data-nifc.opendata.arcgis.com",
        steward="National Interagency Fire Center (NIFC)",
        tribal_data=False,
        license="Public domain (federal government)",
        attribution="National Interagency Fire Center, opendata.arcgis.com",
    ),
    "mtbs": DataSource(
        name="Monitoring Trends in Burn Severity (MTBS)",
        url="https://www.mtbs.gov",
        steward="USGS / USDA Forest Service",
        tribal_data=False,
        license="Public domain (federal government)",
        attribution="Eidenshink et al. (2007). MTBS. USGS/USFS.",
    ),
    "bia_tribal_boundaries": DataSource(
        name="BIA Land Area Representations",
        url="https://biamaps.doi.gov",
        steward="Bureau of Indian Affairs (BIA)",
        tribal_data=True,
        license="Public domain (federal government)",
        ocap_notes=(
            "Tribal boundary data originates from federal records. "
            "Boundaries may not reflect tribal nations' own definitions of territory. "
            "Consult with individual tribes for authoritative boundary information."
        ),
        attribution="Bureau of Indian Affairs, BIA National LAR dataset.",
    ),
    "census_aiannh": DataSource(
        name="Census TIGER AIANNH",
        url="https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html",
        steward="US Census Bureau",
        tribal_data=True,
        license="Public domain (federal government)",
        ocap_notes=(
            "Census-defined boundaries are for statistical purposes only. "
            "They do not represent legal jurisdiction or tribal self-definition."
        ),
        attribution="US Census Bureau, TIGER/Line Shapefiles, 2023.",
    ),
    "native_land_digital": DataSource(
        name="Native Land Digital",
        url="https://native-land.ca",
        steward="Native Land Digital (non-profit)",
        tribal_data=True,
        license="CC BY-NC 4.0",
        ocap_notes=(
            "Native Land Digital collaborates with Indigenous communities, "
            "but maps are not authoritative legal representations. "
            "Attribution required. Non-commercial use only."
        ),
        attribution="Native Land Digital. native-land.ca. CC BY-NC 4.0.",
        use_restrictions=(
            "Non-commercial use only. Do not use for legal or jurisdictional claims. "
            "Credit required in all publications."
        ),
    ),
    "fema_nri": DataSource(
        name="FEMA National Risk Index",
        url="https://hazards.fema.gov/nri/",
        steward="Federal Emergency Management Agency (FEMA)",
        tribal_data=False,
        license="Public domain (federal government)",
        attribution="FEMA National Risk Index, 2023.",
    ),
    "wui": DataSource(
        name="USDA WUI Dataset",
        url="https://www.fs.usda.gov/rds/archive/catalog/RDS-2015-0047-2",
        steward="USDA Forest Service",
        tribal_data=False,
        license="Public domain (federal government)",
        attribution="Radeloff et al. (2018). USDA Forest Service Research Data Archive.",
    ),
}


# Sovereignty acknowledgment 

def print_data_acknowledgment(source_keys: Optional[list[str]] = None) -> None:
    """
    Print data sovereignty acknowledgment for a notebook.
    Call at the top of any notebook that uses Tribal data sources.

    Parameters
    ----------
    source_keys : list of keys from SOURCES dict. If None, prints all Tribal sources.
    """
    keys = source_keys or [k for k, v in SOURCES.items() if v.tribal_data]

    print("=" * 70)
    print("DATA SOVEREIGNTY ACKNOWLEDGMENT")
    print("=" * 70)
    print(
        "This analysis uses data that describes Indigenous and Tribal lands, "
        "communities, and fire histories. We recognize that:\n"
        "\n"
        "• Tribal nations are sovereign governments with the right to control\n"
        "  data about their own communities and territories (OCAP® principles).\n"
        "\n"
        "• Federal and third-party datasets may not reflect Tribal Nations'\n"
        "  own definitions of territory, governance, or cultural practice.\n"
        "\n"
        "• This work is intended to support — not replace — Tribal-led\n"
        "  fire science and land management.\n"
    )
    print("Data sources used:")
    for key in keys:
        src = SOURCES.get(key)
        if src:
            print(f"  • {src.name} — {src.steward}")
            if src.ocap_notes:
                print(f"    Note: {src.ocap_notes}")
            if src.use_restrictions:
                print(f"    ⚠ Restrictions: {src.use_restrictions}")
            src.warn_if_restricted()
    print("=" * 70)


def generate_citations(source_keys: list[str]) -> str:
    """Return a formatted citation block for use in notebooks or reports."""
    lines = ["References / Data Sources", "-" * 40]
    for key in source_keys:
        src = SOURCES.get(key)
        if src:
            lines.append(f"- {src.citation()}")
        else:
            lines.append(f"- [Unknown source: {key}]")
    return "\n".join(lines)


# Traditional Ecological Knowledge (TEK) disclaimer

TEK_DISCLAIMER = """
Traditional Ecological Knowledge (TEK) Notice
----------------------------------------------
Some analyses in this project draw on or are informed by Indigenous fire
stewardship practices and Traditional Ecological Knowledge. TEK belongs to
the communities that hold it. It is shared here only as general context,
not as data to be extracted, quantified, or used outside the specific
collaborative agreements under which it was shared.

If you are building on this work, consult directly with the relevant
Tribal Nations before incorporating TEK into new analyses or publications.
"""


def print_tek_disclaimer() -> None:
    """Print the TEK disclaimer. Use in indigenous_fire_stewardship.ipynb."""
    print(TEK_DISCLAIMER)
