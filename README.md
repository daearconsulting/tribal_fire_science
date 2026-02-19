# Tribal Fire Mapping & Modeling: North America Datasets

This repository provides a curated reference of **open datasets, tools, and workflows** that support **Tribal-led fire management, mapping, modeling, and research** across North America. The focus is on **spatial fire science** (fire history, fuels, weather, and modeling inputs) while explicitly respecting **Tribal data sovereignty, governance, and ethical use**.

## Quick Links

- [Workflows](#workflows)
- [Datasets](#base-geospatial-layers)
- [Analytical Tools & Platforms](#analytical-tools--platforms)
- [Ethical and Governance Considerations](#data-access--governance)
- [License](#license-and-intent)

## Purpose and Scope

This resource is intended to:
- Support **Tribal Nations and Indigenous communities** in wildfire planning, cultural burning, and resilience work
- Enable **reproducible, transparent fire modeling** using open tools
- Reduce reliance on extractive or proprietary platforms
- Encourage **reciprocity and accountability** when software is used in networked or hosted services

## Base Geospatial Layers

| Layer | Source | Coverage | Notes |
|------|-------|----------|-------|
| Tribal Lands / Reservations | **[BIA Tribal Boundaries][bia]**, **[Native Land Digital][native-land]** | U.S., Canada | Define sovereign lands and cultural areas. Always confirm with local Tribal GIS offices. |
| Elevation / Terrain | **[USGS 3DEP][usgs-3dep]**, **[SRTM][srtm]** | North America | Use for slope, aspect, and terrain-driven fire spread modeling. |
| Hydrology / Watersheds | **[USGS NHDPlus][nhdplus]** | Continental | Important for fire breaks, riparian zones, and smoke transport. |
| Land Cover / Vegetation | **[LANDFIRE EVT/EVC][landfire]**, **[NLCD][nlcd]**, **[ESA CCI Land Cover][cci]** | North America | Vegetation composition and structure for fuels and fire behavior modeling. |

## Fire History & Activity

| Dataset | Description | Source | Temporal Coverage |
|-------|-------------|--------|------------------|
| MTBS | Burn severity and perimeters for large fires | **[MTBS][mtbs]** | 1984–present |
| NIFC Historical Fire Perimeters | National multi-agency fire perimeter dataset | **[NIFC][nifc]** | 1990–present |
| FRAP Fire Perimeters | Western U.S. wildfire polygons | **[CAL FIRE FRAP][frap]** | 1878–present |
| Canadian Wildland Fire Information System | National fire database and near-real-time maps | **[CWFIS][cwfis]** | 1980–present |
| NASA FIRMS (MODIS & VIIRS) | Daily active fire detections (global) | **[NASA FIRMS][firms]** | 2000–present |

## Fuels, Vegetation, and Fire Behavior Inputs

| Dataset | Description | Source |
|-------|-------------|--------|
| LANDFIRE Fuel Models (FBFM40, FCCS) | Fire behavior fuel models (U.S.) | **[LANDFIRE][landfire]** |
| USFS Forest Inventory and Analysis (FIA) | Tree composition and structure data | **[FIA][fia]** |
| Canadian Forest Service Fuel Type Maps | National fuel classifications | **[NRCan Open Data][nrcan]** |
| NDVI / EVI Time Series | Vegetation greenness and drought stress | **[MODIS][modis]**, **[Sentinel-2][sentinel2]** via **[Google Earth Engine][gee]** |

## Weather and Climate

| Dataset | Description | Source | Spatial / Temporal Resolution |
|-------|-------------|--------|-------------------------------|
| GRIDMET | Daily gridded weather data | **[GRIDMET][gridmet]** | 4 km; 1979–present |
| PRISM | Historical and near-real-time climate data | **[PRISM][prism]** | 4 km; 1895–present |
| RAWS | Remote Automated Weather Stations | **[MesoWest RAWS][raws]** | Point-based; live |
| North American Drought Monitor | Tri-national drought synthesis | **[NADM][nadm]** | Monthly |
| NARR / ERA5 Reanalysis | Atmospheric variables for modeling | **[NOAA NARR][narr]**, **[ERA5][era5]** | Hourly to 3-hourly |

## Modeling-Ready Inputs
For use with **[FlamMap][flammap]**, **[Behave7][behave7]**, or **[OpenWFM][openwfm]**.

| Input Layer | Typical Source |
|-----------|----------------|
| Elevation / Slope / Aspect | USGS DEM or SRTM |
| Surface Fuels | LANDFIRE Fuel Models |
| Canopy Cover / Height / Base Height | LANDFIRE or FIA |
| Wind & Weather Grids | GRIDMET or RAWS |
| Moisture / Drought Indices | PRISM, GRIDMET, NADM |

## Cultural and Ecological Integration (With Permission)

| Data Type | Source / Method | Notes |
|---------|----------------|-------|
| Cultural Burning Sites / Traditional Use Areas | Tribal GIS or Cultural Preservation Offices | Highly sensitive; requires explicit governance agreements. |
| Ecocultural Plant Distributions (e.g., sweetgrass, bear root) | Tribal data, ethnobotany surveys, **[GBIF][gbif]** | Supports fire planning that enables cultural regeneration. |
| Wildlife & Habitat Overlays | **[USGS GAP Analysis][gap]**, **[NatureServe][natureserve]** | Aligns fire management with ecological goals. |

## Analytical Tools & Platforms

| Tool | Use | Access |
|----|-----|--------|
| FARSITE / FlamMap / Behave7 | Fire spread and behavior modeling | **[FireLab][firelab]** |
| ICS-209+ | Aggregated fire incident reports for analysis | **[ICS-209+][ics209]** |
| FiredPy | Python CLI for classifying fire events from the MODIS Burned Area Product. | **[FiredPy][firedpy]** |
| QGIS / ArcGIS Pro | Spatial analysis and map creation | Open-source or licensed |
| Google Earth Engine | Cloud-based remote sensing and trend analysis | Free for research |
| Python / R Packages | Data processing and modeling (`rasterio`, `geemap`, `terra`, `sf`) | Reproducible workflows |
| Indigenous Data Cube Framework | EO data under Tribal governance | Indigenous data sovereignty-aligned, customizable |


## Data Access & Governance

This repository **does not assert authority over Tribal data**. Any inclusion of culturally significant, sensitive, or place-based knowledge **must be governed by the relevant Tribal Nation(s)**.

Users are expected to:

- Establish **MOUs or Data Governance Agreements** before mapping cultural sites
- Apply the **CARE Principles**: Collective Benefit, Authority to Control, Responsibility, Ethics
- Respect **OCAP®** (Ownership, Control, Access, Possession) for First Nations data in Canada
- Maintain **Tribal control over access, sharing, and reuse** of sensitive spatial layers

Open data does **not** imply unrestricted use.

## To adapt this analysis for a new location:
1. Replace data in data folder
2. Update configuration variables 
3. Re-run pipeline

## Workflows
Workflows for Tribal fire modeling are documented in **[workflows.md](https://github.com/daearconsulting/Tribal_fire_science/blob/main/workflows.md)**.  
This includes:

- Historical fire analysis & risk mapping  
- Fire behavior simulation  
- Cultural & ecological impact analysis  
- Real-time fire monitoring & early warning  
- Prescribed burn planning & optimization  
- Climate change & fire regime projection  
- Multi-scale decision support dashboards  

## License and Intent
This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0-or-later)**. 
The intent of this license is to ensure the software remains **freely available for Tribal Nations and Indigenous communities**, while preventing **extractive commercial use without contributing improvements back**.
See the `LICENSE` file for full terms.

## External Data & Tool References
[bia]: https://www.bia.gov/bia/ots/dris/bogs
[native-land]: https://native-land.ca
[usgs-3dep]: https://www.usgs.gov/3d-elevation-program
[srtm]: https://www.earthdata.nasa.gov/data/instruments/srtm/data-access-tools
[nhdplus]: https://www.epa.gov/waterdata/nhdplus-national-hydrography-dataset-plus
[chs]: https://www.charts.gc.ca
[landfire]: https://landfire.gov
[nlcd]: https://www.mrlc.gov
[cci]: https://www.esa-landcover-cci.org
[mtbs]: https://www.mtbs.gov
[nifc]: https://data-nifc.opendata.arcgis.com
[frap]: https://frap.fire.ca.gov
[cwfis]: https://cwfis.cfs.nrcan.gc.ca
[firms]: https://firms.modaps.eosdis.nasa.gov
[fia]: https://research.fs.usda.gov/programs/fia#data-and-tools
[nrcan]: https://natural-resources.canada.ca
[modis]: https://modis.gsfc.nasa.gov
[sentinel2]: https://browser.dataspace.copernicus.eu/?zoom=11&lat=45.36638&lng=12.49832&themeId=DEFAULT-THEME&visualizationUrl=U2FsdGVkX19cM7M9JGT%2F5YjyMebnBleEP4c7p0edvL3GFdexxtXHjlPR1gjilU9MzKmGyrm4PHbDK6JStx3qsH42QR%2BSh5TjlWwPEvIQXWsPAYBmqCsr1HXfL6sd0Yq6&datasetId=S2_L1C_CDAS&fromTime=2023-02-07T00%3A00%3A00.000Z&toTime=2023-02-07T23%3A59%3A59.999Z&layerId=1_TRUE_COLOR&demSource3D="MAPZEN"&cloudCoverage=10&dateMode=SINGLE
[gee]: https://earthengine.google.com
[gridmet]: https://www.climatologylab.org/gridmet.html
[prism]: https://prism.oregonstate.edu
[raws]: https://mesowest.utah.edu
[nadm]: https://droughtmonitor.unl.edu
[narr]: https://www.ncei.noaa.gov/products/weather-climate-models/narr
[era5]: https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5
[flammap]: https://research.fs.usda.gov/firelab/projects/flammap
[behave7]: https://www.frames.gov/behave/home
[openwfm]: https://github.com/openwfm
[gbif]: https://www.gbif.org
[gap]: https://www.usgs.gov/programs/gap-analysis-project
[natureserve]: https://explorer.natureserve.org
[firelab]: https://research.fs.usda.gov/firelab/products/dataandtools



