"""
sovereignty.py — Data governance, attribution, and sovereignty helpers.

This module exists because Indigenous data sovereignty principles should not be
scattered across notebooks as comments. They belong in shared, versioned code.

Three complementary frameworks guide data governance in this project:

OCAP® Principles (First Nations Information Governance Centre)
  Ownership   — Tribal Nations own their collective data and cultural knowledge
  Control     — Nations control how data is used, interpreted, and shared
  Access      — Nations have the right to access data about their communities
  Possession  — Nations should physically hold or steward data about themselves
  Reference   : https://fnigc.ca/ocap-training/

CARE Principles for Indigenous Data Governance (Global Indigenous Data Alliance)
  Collective Benefit  — Data ecosystems should enable Indigenous peoples to
                        benefit from their data
  Authority to Control — Indigenous peoples' rights and interests in Indigenous
                        data must be recognised and their authority to control
                        such data empowered
  Responsibility      — Those working with Indigenous data have a responsibility
                        to share how that data is used
  Ethics              — Indigenous peoples' rights and wellbeing should be the
                        primary concern across the data lifecycle
  Reference           : https://www.gida-global.org/care

FAIR Principles (FORCE11)
  Findable     — Data and metadata are easy to find for humans and machines
  Accessible   — Data is retrievable using open, universal protocols
  Interoperable — Data uses standard formats and vocabularies
  Reusable     — Data has clear licensing and provenance documentation
  Reference    : https://www.go-fair.org/fair-principles/

Relationship between frameworks
FAIR establishes the open science baseline. CARE and OCAP® establish that
Indigenous data requires additional governance that FAIR alone does not address.
A dataset can be fully FAIR and still violate Indigenous data sovereignty if it
was collected without consent, strips cultural context, or enables harmful use.
In this project, FAIR governs technical data standards; CARE and OCAP® govern
ethical obligations to Tribal Nations and communities.

Additional references
- UNDRIP Article 31: https://www.un.org/development/desa/indigenouspeoples/
- US Indigenous Data Sovereignty Network: https://usindigenousdata.org
- GIDA CARE Principles: https://www.gida-global.org/care
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import warnings


# Data source registry 

@dataclass
class DataSource:
    """
    Metadata for a dataset used in this project.

    Parameters
    name             : Human-readable name
    url              : Authoritative source URL
    steward          : Organization responsible for the data
    tribal_data      : True if the dataset contains Indigenous/Tribal attributes
    license          : License or terms of use
    ocap_notes       : How this dataset relates to OCAP® principles
    care_notes       : How this dataset relates to CARE principles
    fair_notes       : How this dataset relates to FAIR principles
    attribution      : Required attribution string for publication
    use_restrictions : Any restrictions on how data may be used
    """
    name: str
    url: str
    steward: str
    tribal_data: bool = False
    license: str = ""
    ocap_notes: str = ""
    care_notes: str = ""
    fair_notes: str = ""
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
        fair_notes="Publicly accessible, machine-readable GeoJSON. Updated continuously.",
        attribution="National Interagency Fire Center, opendata.arcgis.com",
    ),
    "mtbs": DataSource(
        name="Monitoring Trends in Burn Severity (MTBS)",
        url="https://www.mtbs.gov",
        steward="USGS / USDA Forest Service",
        tribal_data=False,
        license="Public domain (federal government)",
        fair_notes="Findable and accessible via direct download. Standard shapefile format.",
        attribution="Eidenshink et al. (2007). MTBS. USGS/USFS.",
    ),
    "bia_tribal_boundaries": DataSource(
        name="BIA Land Area Representations",
        url="https://biamaps.doi.gov",
        steward="Bureau of Indian Affairs (BIA)",
        tribal_data=True,
        license="Public domain (federal government)",
        ocap_notes=(
            "Tribal boundary data originates from federal records, not Tribal Nations "
            "themselves. Boundaries may not reflect Tribal Nations' own definitions of "
            "territory. Consult with individual Tribes for authoritative boundary information."
        ),
        care_notes=(
            "Federal boundary data was not produced under Tribal Authority to Control. "
            "Use for analytical context only — not for legal, jurisdictional, or "
            "policy claims without Tribal review and consent."
        ),
        fair_notes="Accessible via WFS endpoint. Schema is consistent across vintages.",
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
            "They do not represent legal jurisdiction or Tribal self-definition. "
            "Tribal Nations were not the primary stewards of this data collection."
        ),
        care_notes=(
            "Census data was collected by the federal government, not under Tribal "
            "Authority to Control. Collective Benefit to Tribal Nations depends on "
            "how results are applied — analysis should serve Tribal interests."
        ),
        fair_notes=(
            "Highly FAIR — versioned annual releases, standard shapefile and GeoJSON "
            "formats, well-documented metadata, open license."
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
            "Native Land Digital collaborates with Indigenous communities and "
            "incorporates community input, but maps are not authoritative legal "
            "representations of Tribal territory."
        ),
        care_notes=(
            "Produced with community input — stronger Collective Benefit and "
            "Authority to Control than federal sources. Non-commercial license "
            "reflects Responsibility to communities. Review ethics of use case "
            "before applying in any policy or legal context."
        ),
        fair_notes=(
            "Accessible via API. CC BY-NC 4.0 license governs reuse. "
            "Attribution required in all publications."
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
        fair_notes="County-level composite scores. Versioned annual releases. Open download.",
        attribution="FEMA National Risk Index, 2023.",
    ),
    "usgs_wbd": DataSource(
        name="USGS Watershed Boundary Dataset (WBD) HUC-8",
        url="https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer",
        steward="US Geological Survey (USGS)",
        tribal_data=False,
        license="Public domain (federal government)",
        fair_notes="REST API, versioned, standard GeoJSON output, national coverage.",
        attribution="USGS National Hydrography Dataset, Watershed Boundary Dataset.",
    ),
    "epa_ecoregions_l3": DataSource(
        name="EPA Level III Ecoregions",
        url="https://geodata.epa.gov/arcgis/rest/services/ORD/NATL_ECO_L3_SIMP/MapServer",
        steward="US Environmental Protection Agency (EPA)",
        tribal_data=False,
        license="Public domain (federal government)",
        fair_notes="REST API, GeoJSON, simplified polygon version for web mapping.",
        attribution="Omernik, J.M. & Griffith, G.E. (2014). EPA Ecoregions.",
    ),
    "hifld_fire_stations": DataSource(
        name="HIFLD Fire Stations",
        url="https://hifld-geoplatform.opendata.arcgis.com/datasets/fire-stations",
        steward="Homeland Infrastructure Foundation-Level Data (HIFLD) / DHS",
        tribal_data=False,
        license="Public domain (federal government)",
        fair_notes=(
            "Accessible via ArcGIS REST API. Updated periodically. "
            "Includes federal, state, local, and some Tribal fire stations."
        ),
        attribution="HIFLD Fire Stations. U.S. Department of Homeland Security.",
    ),
    "gridmet": DataSource(
        name="gridMET Daily Surface Meteorological Data",
        url="https://www.climatologylab.org/gridmet.html",
        steward="University of Idaho Climatology Lab",
        tribal_data=False,
        license="Public domain",
        fair_notes=(
            "Highly FAIR — OPeNDAP access, consistent NetCDF format, "
            "DOI-registered, 1979-present daily 4km CONUS coverage."
        ),
        attribution="Abatzoglou, J.T. (2013). gridMET. Int. J. Climatology.",
    ),
    "wui": DataSource(
        name="USDA WUI Dataset",
        url="https://www.fs.usda.gov/rds/archive/catalog/RDS-2015-0047-2",
        steward="USDA Forest Service",
        tribal_data=False,
        license="Public domain (federal government)",
        fair_notes="Archived with DOI. Manual download required — not available via API.",
        attribution="Radeloff et al. (2018). USDA Forest Service Research Data Archive.",
    ),
}


# Sovereignty acknowledgment

def print_data_acknowledgment(source_keys: Optional[list[str]] = None) -> None:
    """
    Print data sovereignty acknowledgment for a notebook.
    Call at the top of any notebook that uses Tribal data sources.

    Parameters
    source_keys : list of keys from SOURCES dict. If None, prints all Tribal sources.
    """
    keys = source_keys or [k for k, v in SOURCES.items() if v.tribal_data]

    print("=" * 70)
    print("DATA SOVEREIGNTY ACKNOWLEDGMENT")
    print("=" * 70)
    print(
        "This analysis uses data that describes Indigenous and Tribal lands,\n"
        "communities, and fire histories. This project is guided by three\n"
        "complementary data governance frameworks:\n"
        "\n"
        "OCAP® — Tribal Nations own, control, access, and possess data about\n"
        "  their own communities and territories.\n"
        "  Reference: https://fnigc.ca/ocap-training/\n"
        "\n"
        "CARE  — Data use must deliver Collective Benefit to Indigenous peoples,\n"
        "  respect their Authority to Control, uphold Responsibility to communities,\n"
        "  and center Ethics across the full data lifecycle.\n"
        "  Reference: https://www.gida-global.org/care\n"
        "\n"
        "FAIR  — Data is Findable, Accessible, Interoperable, and Reusable.\n"
        "  FAIR governs technical standards; CARE and OCAP® govern the ethical\n"
        "  obligations to Tribal Nations that FAIR alone does not address.\n"
        "  Reference: https://www.go-fair.org/fair-principles/\n"
        "\n"
        "We recognize that:\n"
        "\n"
        "• Tribal Nations are sovereign governments with the right to control\n"
        "  data about their own communities and territories.\n"
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
                print(f"    OCAP®: {src.ocap_notes}")
            if src.care_notes:
                print(f"    CARE : {src.care_notes}")
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
Some analyses in this project draw on or are informed by Indigenous fire
stewardship practices and Traditional Ecological Knowledge. TEK belongs to
the communities that hold it. It is shared here only as general context —
not as data to be extracted, quantified, or used outside the specific
collaborative agreements under which it was shared.

Under CARE principles, Tribal Nations hold Authority to Control how their
knowledge is represented and used. Under OCAP®, Traditional Knowledge is
Owned and Possessed by the Nation or community that holds it.

If you are building on this work, consult directly with the relevant
Tribal Nations before incorporating TEK into new analyses or publications.
"""


def print_tek_disclaimer() -> None:
    """Print the TEK disclaimer. Use in indigenous_fire_stewardship.ipynb."""
    print(TEK_DISCLAIMER)
