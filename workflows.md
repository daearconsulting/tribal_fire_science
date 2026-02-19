Tribal Fire Science Workflows
This document outlines workflows for Tribal-led fire research, modeling, and management, combining historical fire data, real-time monitoring, and culturally/ecologically sensitive planning.

Tribal Fire Mapping & Modeling Workflows

Historical Fire Analysis & Risk Mapping
Goal: Understand past fire behavior to predict areas at higher risk.

Inputs:

MTBS, NIFC, FRAP, CWFIS (historical fire perimeters)
LANDFIRE vegetation/fuel layers
DEM (elevation, slope, aspect)
GRIDMET / PRISM weather data

Workflow:

Compile historical fire perimeters in GIS.
Overlay vegetation, topography, and weather variables.
Calculate fire frequency, burn severity, and fire return intervals.
Generate risk maps highlighting areas prone to future fires.
Use maps for pre-fire planning, community safety zones, or fuel reduction priorities.

Tools: QGIS/ArcGIS, R (raster, sf), Python (geopandas, rasterio)

Fire Behavior Simulation
Goal: Model potential fire spread under specific weather and fuel conditions.

Inputs:

DEM & slope/aspect
LANDFIRE fuel layers or local fuel maps
Wind & humidity from GRIDMET / RAWS
Surface and canopy moisture indices (PRISM, NDVI/EVI)

Workflow:

Preprocess terrain and fuel data for modeling software.
Set weather and wind grids for desired simulation dates.
Run FARSITE or FlamMap simulations for fire spread.
Output maps of fire intensity, spread direction, and burn probability.
Compare multiple scenarios (e.g., drought vs. normal) to inform management.

Use Cases: Prescribed burn planning, emergency response, hazard mitigation

Fire Impact on Cultural & Ecological Resources
Goal: Protect cultural resources and sensitive ecosystems.

Inputs:

Cultural burning sites or traditional use areas (Tribal GIS)
Ecocultural plant distributions (bear root, sweetgrass)
Wildlife habitat overlays
Fire risk maps or simulated fire spread layers

Workflow:

Overlay fire risk / modeled fire spread with culturally sensitive areas.
Identify priority zones for protective fire breaks or controlled burns.
Integrate results into Tribal land stewardship planning.
Update dataset after each fire season for adaptive management.

Use Cases: Preserving sacred plants, wildlife corridors, and heritage sites

Real-Time Fire Monitoring & Early Warning
Goal: Track active fires and predict risks dynamically.

Inputs:

NASA FIRMS (MODIS/VIIRS) active fire detections
RAWS live weather stations
NDVI/EVI vegetation stress indices

Workflow:

Pull daily satellite fire detections and visualize in GIS.
Integrate current weather and wind to predict likely fire expansion.
Generate real-time alert maps for Tribal land managers.
Provide decision support for evacuation or resource allocation.

Tools: Google Earth Engine, QGIS/ArcGIS, Python automated scripts

Prescribed Burn Planning & Optimization
Goal: Use controlled fire to restore ecosystem health and reduce wildfire risk.

Inputs:

LANDFIRE fuel and vegetation layers
Terrain layers
Historical fire frequency and severity maps
Weather forecasts (GRIDMET/RAWS)

Cultural priority zones

Workflow:

Identify candidate areas for prescribed burns (low risk to communities, high ecological benefit).
Model fire behavior under forecasted conditions using FlamMap/FARSITE.
Evaluate impact on vegetation, soils, and culturally important plants.
Schedule and execute burns safely, document outcomes for adaptive management.

Use Cases: Grassland restoration, reducing invasive species, supporting cultural plant growth

Climate Change & Fire Regime Projection
Goal: Assess how changing climate affects fire frequency and intensity.

Inputs:

Historical fire perimeters
PRISM / GRIDMET long-term climate data
NARR / ERA5 reanalysis for atmospheric trends
Fuel layers

Workflow:

Analyze historical fire trends in relation to climate variables.
Model future fire scenarios using projected climate data.
Map high-risk areas under multiple emission scenarios.

Support Tribal climate adaptation planning.

Multi-Scale Decision Support Dashboard
Goal: Create a centralized tool for Tribal fire management.

Inputs:

Fire risk maps, historical fire perimeters, active fire detections
Weather, terrain, and vegetation data
Cultural and ecological overlays

Workflow:

Combine all layers into a web GIS or dashboard (ArcGIS Online, Google Earth Engine Apps, or custom Python web app with Dash/Streamlit).
Allow partners to query risks, simulate scenarios, or plan prescribed burns.
Integrate alerts for active fires and forecasted conditions.

Maintain data sovereignty — host on Tribal servers or secure cloud space.

Notes
These workflows are modular — start with historical analysis and build toward real-time monitoring or predictive modeling.
Combining fire science datasets with cultural/ecological layers ensures holistic Tribal decision-making.
Using open-source tools (QGIS, Python, Google Earth Engine) keeps projects reproducible and accessible.

