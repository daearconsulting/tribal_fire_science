## Tribal Fire Science Workflows

This document outlines workflows for Tribal-led fire research, modeling, and management, combining historical fire data, real-time monitoring, and culturally and ecologically sensitive planning.

## Tribal Fire Mapping & Modeling Workflows

## Historical Fire Analysis & Risk Mapping

**Goal:** Understand past fire behavior to predict areas at higher risk.

### Inputs

- MTBS, NIFC, FRAP, CWFIS (historical fire perimeters)  
- LANDFIRE vegetation/fuel layers  
- DEM (elevation, slope, aspect)  
- GRIDMET / PRISM weather data  

### Workflow

1. Compile historical fire perimeters in GIS.  
2. Overlay vegetation, topography, and weather variables.  
3. Calculate fire frequency, burn severity, and fire return intervals.  
4. Generate risk maps highlighting areas prone to future fires.  
5. Use maps for pre-fire planning, community safety zones, or fuel reduction priorities.

**Tools:** QGIS / ArcGIS, R (`raster`, `sf`), Python (`geopandas`, `rasterio`)

## Fire Behavior Simulation

**Goal:** Model potential fire spread under specific weather and fuel conditions.

### Inputs

- DEM & slope/aspect  
- LANDFIRE fuel layers or local fuel maps  
- Wind & humidity from GRIDMET / RAWS  
- Surface and canopy moisture indices (PRISM, NDVI/EVI)  

### Workflow

1. Preprocess terrain and fuel data for modeling software.  
2. Set weather and wind grids for desired simulation dates.  
3. Run FARSITE or FlamMap simulations for fire spread.  
4. Output maps of fire intensity, spread direction, and burn probability.  
5. Compare multiple scenarios (e.g., drought vs. normal) to inform management.

**Use Cases:** Prescribed burn planning, emergency response, hazard mitigation

## Fire Impact on Cultural & Ecological Resources

**Goal:** Protect cultural resources and sensitive ecosystems.

### Inputs

- Cultural burning sites or traditional use areas (Tribal GIS)  
- Ecocultural plant distributions (bear root, sweetgrass)  
- Wildlife habitat overlays  
- Fire risk maps or simulated fire spread layers  

### Workflow

1. Overlay fire risk / modeled fire spread with culturally sensitive areas.  
2. Identify priority zones for protective fire breaks or controlled burns.  
3. Integrate results into Tribal land stewardship planning.  
4. Update dataset after each fire season for adaptive management.

**Use Cases:** Preserving sacred plants, wildlife corridors, and heritage sites

## Real-Time Fire Monitoring & Early Warning

**Goal:** Track active fires and predict risks dynamically.

### Inputs

- NASA FIRMS (MODIS/VIIRS) active fire detections  
- RAWS live weather stations  
- NDVI/EVI vegetation stress indices  

### Workflow

1. Pull daily satellite fire detections and visualize in GIS.  
2. Integrate current weather and wind to predict likely fire expansion.  
3. Generate real-time alert maps for Tribal land managers.  
4. Provide decision support for evacuation or resource allocation.

**Tools:** Google Earth Engine, QGIS / ArcGIS, Python automated scripts

## Prescribed Burn Planning & Optimization

**Goal:** Use controlled fire to restore ecosystem health and reduce wildfire risk.

### Inputs

- LANDFIRE fuel and vegetation layers  
- Terrain layers  
- Historical fire frequency and severity maps  
- Weather forecasts (GRIDMET / RAWS)  
- Cultural priority zones  

### Workflow

1. Identify candidate areas for prescribed burns  
   - Low risk to communities  
   - High ecological benefit  

2. Model fire behavior under forecasted conditions using FlamMap or FARSITE.  
3. Evaluate impact on vegetation, soils, and culturally important plants.  
4. Schedule and execute burns safely.  
5. Document outcomes for adaptive management.

**Use Cases:**  
- Grassland restoration  
- Reducing invasive species  
- Supporting cultural plant growth  

## Climate Change & Fire Regime Projection

**Goal:** Assess how changing climate affects fire frequency and intensity.

### Inputs

- Historical fire perimeters  
- PRISM / GRIDMET long-term climate data  
- NARR / ERA5 reanalysis for atmospheric trends  
- Fuel layers  

### Workflow

1. Analyze historical fire trends in relation to climate variables.  
2. Model future fire scenarios using projected climate data.  
3. Map high-risk areas under multiple emission scenarios.  
4. Support Tribal climate adaptation planning.

## Multi-Scale Decision Support Dashboard

**Goal:** Create a centralized tool for Tribal fire management.

### Inputs

- Fire risk maps  
- Historical fire perimeters  
- Active fire detections  
- Weather, terrain, and vegetation data  
- Cultural and ecological overlays  

### Workflow

1. Combine all layers into a web GIS or dashboard:  
   - ArcGIS Online  
   - Google Earth Engine Apps  
   - Custom Python web app (Dash / Streamlit)  

2. Allow partners to:  
   - Query risks  
   - Simulate scenarios  
   - Plan prescribed burns  

3. Integrate alerts for active fires and forecasted conditions.  
4. Maintain data sovereignty — host on Tribal servers or secure cloud space.

## Notes

- These workflows are modular; start with historical analysis and build toward real-time monitoring or predictive modeling.  
- Combining fire science datasets with cultural and ecological layers ensures holistic Tribal decision-making.  
- Using open-source tools (QGIS, Python, Google Earth Engine) keeps projects reproducible and accessible.
