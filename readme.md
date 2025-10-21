# Climate Analysis Project

Python project for analyzing atmospheric CO₂ and surface temperature anomalies. It reads raw and processed datasets, creates combined dataframes, and generates visualizations for climate research and exploration.

## Data Sources

[OCO2 GES DISC, NASA L2](https://disc.gsfc.nasa.gov/datasets/OCO2_L2_Standard_11r/summary) : Column-averaged CO₂ (XCO₂) measurements with temporal and geospatial metadata. The data was transformed from HDF5 format into a processable dataframe for analysis.

[GISTEMP, NASA](http://data.giss.nasa.gov/gistemp/) : Surface temperature anomalies with temporal and geospatial metadata. Values are expressed in K.

## Visualizations (wip)

Temperature anomaly data is clustered by geographic proximity using the **K-Means algorithm**. Locations within a user-specified latitude/longitude range are grouped into a configurable number of clusters (default: 5). This allows for exploration of regional anomaly patterns over time.  

The figure legend indicates the approximate geographic centroid of each cluster.

![Temperature anomalies by region](outputs/plots/tempanomalies.png)

## Notes

- CO₂ values are in parts per million (ppm).  
- Temperature anomalies are relative to the baseline period provided by GISTEMP.  
- Figures are saved to `outputs/plots/` with configurable resolution and size.  
- Future work may include more advanced clustering methods and temporal trend analysis.