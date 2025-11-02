# Climate Analysis Project

Python project for analyzing atmospheric CO₂ and surface temperature anomalies. It reads raw and processed datasets, creates combined dataframes, and generates visualizations for climate research and exploration.

## Data Sources

[OCO2 GES DISC, NASA L2](https://disc.gsfc.nasa.gov/datasets/OCO2_L2_Standard_11r/summary) : Column-averaged CO₂ (XCO₂) measurements with temporal and geospatial metadata. The data was transformed from HDF5 format into a processable dataframe for analysis.

[GISTEMP, NASA](http://data.giss.nasa.gov/gistemp/) : Surface temperature anomalies with temporal and geospatial metadata. Values are expressed in K.

## Visualizations

Several visualizations are generated from OCO2 CO₂ measurements:

<div style="text-align: center;">
  <img src="outputs/plots/co2_sparse_heatmap.png" alt="CO₂ concentration heatmap" width="600"/>
  <p><b>Interpolated CO₂ Heatmap from Sparse Measurements</b><br/>
  Shows interpolated XCO₂ levels with black circles indicating actual satellite measurement locations.</p>
</div>

<div style="display: flex; justify-content: space-between;">
  <div style="flex: 1; text-align: center;">
    <img src="outputs/plots/co2_highest.png" alt="Highest CO₂ areas" width="300"/>
    <p><b>Areas with Highest CO₂ Concentrations</b></p>
  </div>
  <div style="flex: 1; text-align: center;">
    <img src="outputs/plots/co2_lowest.png" alt="Lowest CO₂ areas" width="300"/>
    <p><b>Areas with Lowest CO₂ Concentrations</b></p>
  </div>
</div>

XCO₂ represents the column-averaged CO₂ concentration from ground to upper atmosphere (~60km), measured in parts per million (ppm).

Data exploration notebooks in `01_data_exploration/` download and process NASA L2 NC4 files (2024-2025 satellite readings) with configurable data volume limits.

Temperature anomaly data is clustered by geographic proximity using the **K-Means algorithm**. Locations within a user-specified latitude/longitude range are grouped into a configurable number of clusters (default: 5). This allows for exploration of regional anomaly patterns over time.  

The figure legend indicates the approximate geographic centroid of each cluster.

![Temperature anomalies by region](outputs/plots/tempanomalies.png)

## How to run

### Environment Setup

Prerequisites:

- Conda package manager
- Create environment from file: `conda env create -f environment.yml`
- Activate environment: `conda activate climate_analysis`

### Run the CLI entrypoint (main.py)

Typical usage:

- From project root:
  - `python src/main.py`  
  - Example with common options:  
        `python src/main.py --year-range 5 --lon -122.4194 --lat 37.7749 --loc-range 10`

Notes:

- Run `python src/main.py --help` to see all supported arguments
- Key arguments:
  - `--year-range`: Number of years to analyze (default: 1)
  - `--lon`: Longitude coordinate to center analysis (optional)
  - `--lat`: Latitude coordinate to center analysis (optional)
  - `--loc-range`: Range in degrees around location coordinates (default: 10)
- Output figures are written to `outputs/plots/` by default

### Run Jupyter notebooks / JupyterLab

Prerequisites:

- JupyterLab is included in environment.yml
- Ensure conda environment is activated: `conda activate climate_analysis`

Start JupyterLab with the project config:

- From project root:
  - `jupyter lab --config=.jupyter/jupyter_lab_config.py`

## Notes

- CO₂ values are in parts per million (ppm)
- Temperature anomalies are relative to the baseline period provided by GISTEMP
- Figures are saved to `outputs/plots/` with configurable resolution and size
- Future work may include more advanced clustering methods and temporal trend analysis
