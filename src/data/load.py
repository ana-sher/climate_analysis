from datetime import datetime
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from typing import Literal, Optional
import h5py
import earthaccess

from src.config import DATA_DIR, TEMPANOMALIES, CO2, settings


def load_co2() -> pd.DataFrame:
    return load_csv(CO2)


def load_tempanomalies() -> pd.DataFrame:
    return load_csv(TEMPANOMALIES)


def read_raw_tempanomalies(
    year_from: int, lat_min: float, lat_max: float, lon_min: float, lon_max: float
) -> pd.DataFrame:
    """
    Reads raw GISTEMP temperature anomalies data from local NetCDF files.
    Data source structure processed: GISTEMP, NASA http://data.giss.nasa.gov/gistemp/
    Structure:
        Dims: time, nv, lat, lon
        Vars: time_bnds, tempanomaly (K)

    Parameters:
        year_from (int): Year from which to read data
        lat_min (float): Minimum latitude
        lat_max (float): Maximum latitude
        lon_min (float): Minimum longitude
        lon_max (float): Maximum longitude
    Returns:
        pd.DataFrame: DataFrame containing tempanomaly (K) by lat, lon, time
    """
    temp_anomalies_ds = _get_raw_filenames_dataset("nc", prefix="gistemp")

    temp_anomalies_ds = temp_anomalies_ds.sel(
        time=temp_anomalies_ds["time"].dt.year >= year_from
    )
    temp_anomalies_ds = temp_anomalies_ds.sel(
        lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max)
    )
    # temp_anomalies_ds = temp_anomalies_ds.dropna(
    #     dim='time', subset=['tempanomaly'])

    temp_anomalies_df = temp_anomalies_ds["tempanomaly"].to_dataframe().reset_index()
    return temp_anomalies_df


def read_raw_co2(
    year_from: int, lat_min: float, lat_max: float, lon_min: float, lon_max: float
) -> pd.DataFrame:
    """
    Reads raw OCO-2 CO2 data from local HDF5 files.
    Data source structure processed: GES DISC, NASA L2 data https://disc.gsfc.nasa.gov/datasets/OCO2_L2_Standard_11r/summary
    Structure:
        Dims: retrieval (artificially created)
        Vars: xco2 (ppm)
        Coords: time, lat, lon

    Parameters:
        year_from (int): Year from which to read data
        lat_min (float): Minimum latitude
        lat_max (float): Maximum latitude
        lon_min (float): Minimum longitude
        lon_max (float): Maximum longitude
    Returns:
        pd.DataFrame: DataFrame containing xco2 (ppm) by lat, lon, time
    """
    path = DATA_DIR / "raw"
    files = list(Path(path).glob(f"oco*.h5"))
    if not files:
        raise FileNotFoundError("No files found for co2 reading")
    datasets = [_get_oco_file_ds(path / file.name) for file in files]

    if len(datasets) == 1:
        return datasets[0]["xco2"].to_dataframe().reset_index()
    combined = xr.concat(datasets, dim="retrieval")
    combined = combined.assign_coords(
        time=(
            "retrieval",
            pd.to_datetime(combined["time"].values, utc=True).tz_localize(None),
        )
    )

    co2_ds = combined.where(combined["time"].dt.year >= year_from, drop=True)
    co2_ds = co2_ds.where(
        (co2_ds["lat"] >= lat_min)
        & (co2_ds["lat"] <= lat_max)
        & (co2_ds["lon"] >= lon_min)
        & (co2_ds["lon"] <= lon_max),
        drop=True,
    )

    co2_df = co2_ds["xco2"].to_dataframe().reset_index()
    return co2_df


def read_remote_co2(
    year_from: int,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    limit: int = 25,
    locally: bool = True,
) -> pd.DataFrame:
    """
    Reads remote OCO-2 CO2 data using Earthdata Access.
    Data source structure processed: GES DISC, NASA L2 data https://disc.gsfc.nasa.gov/datasets/OCO2_L2_Lite_FP_11.2r/summary
    Structure:
        Dims: sounding_id
        Vars: xco2 (ppm), xco2_quality_flag
        Coords: time, latitude, longitude

    Parameters:
        year_from: Year from which to read data
        lat_min: Minimum latitude
        lat_max: Maximum latitude
        lon_min: Minimum longitude
        lon_max: Maximum longitude
        limit: Maximum number of files to download
        locally: To save processing raw files locally or work with s3
    Returns:
        pd.DataFrame: DataFrame containing xco2 (ppm) by lat, lon, time
    """
    path = DATA_DIR / "raw"
    year_now = datetime.now().year
    earthaccess.login()
    results = earthaccess.search_data(
        short_name="OCO2_L2_Lite_FP",
        temporal=(f"{year_from}-01-01", f"{year_now}-01-02"),
        bounding_box=(lon_min, lat_min, lon_max, lat_max),
    )
    step = int(math.ceil(len(results) / limit))
    if locally:
        files = earthaccess.download(results[::step], path)
        datasets = [
            xr.open_dataset(path / file.name, engine="netcdf4") for file in files
        ]
        combined = xr.concat(datasets, dim="sounding_id", join="outer")
    else:
        # TODO: implement S3 download because earthaccess does not support saving reference files to S3 yet + outer join (explore)
        combined = earthaccess.open_virtual_mfdataset(
            results[::step],
            reference_dir=f"s3://{settings.S3_BUCKET}/kerchunk_refs/",
            reference_format="parquet",
            xr_combine_nested_kwargs={"concat_dim": "sounding_id", "join": "outer"},
        )

    xco2_ds = combined.where(combined["xco2_quality_flag"] == 0, drop=True)
    xco2_ds = xco2_ds.where(xco2_ds["time"].dt.year >= year_from, drop=True)
    xco2_ds = xco2_ds.where(
        (xco2_ds["latitude"] >= lat_min)
        & (xco2_ds["latitude"] <= lat_max)
        & (xco2_ds["longitude"] >= lon_min)
        & (xco2_ds["longitude"] <= lon_max),
        drop=True,
    )

    xco2_df = (
        xco2_ds[["xco2", "time", "latitude", "longitude"]].to_dataframe().reset_index()
    )
    xco2_df = xco2_df.rename(columns={"latitude": "lat", "longitude": "lon"})

    return xco2_df


def load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / "processed" / f"{filename}.csv"
    return pd.read_csv(path)


def load_parquet(filename: str) -> pd.DataFrame:
    path = DATA_DIR / "processed" / f"{filename}.parquet"
    return pd.read_parquet(path)


def load_netcdf(filename: str, engine: Optional[str] = None) -> xr.Dataset:
    path = DATA_DIR / "raw" / filename
    return xr.open_dataset(path, engine=engine)


def _get_raw_filenames_dataset(
    file_format: Literal["h5", "nc", "nc4"], concat_dim: str = "time", prefix: str = ""
) -> xr.Dataset:
    path = DATA_DIR / "raw"
    if file_format == "h5":
        engine = "h5netcdf"
    elif file_format == "nc" or file_format == "nc4":
        engine = "netcdf4"
    files = list(Path(path).glob(f"{prefix}*.{file_format}"))
    if not files:
        raise FileNotFoundError("No files found matching the pattern")
    datasets = [load_netcdf(file.name, engine) for file in files]
    if len(datasets) == 1:
        return datasets[0]
    combined = xr.concat(datasets, dim=concat_dim)
    return combined


def _load_dataset(node) -> np.ndarray:
    if isinstance(node, h5py.Dataset):
        return node[:]
    elif isinstance(node, np.ndarray):
        return node
    else:
        raise TypeError(f"Expected dataset or array, got {type(node)}")


def _get_oco_file_ds(path: Path) -> xr.Dataset:
    with h5py.File(path, "r") as f:
        keys = list(f.keys())
        if (
            "RetrievalResults" not in keys
            or "RetrievalGeometry" not in keys
            or "RetrievalHeader" not in keys
        ):
            raise ValueError(f"File {path} missing required groups for OCO-2 data")

        retrieval_lat = _load_dataset(f["RetrievalGeometry/retrieval_latitude"])
        retrieval_lon = _load_dataset(f["RetrievalGeometry/retrieval_longitude"])
        retrieval_time = [
            time.decode("utf-8")
            for time in _load_dataset(f["RetrievalHeader/retrieval_time_string"])
        ]

        xco2 = [x * 1e6 for x in _load_dataset(f["RetrievalResults/xco2"])]
        return xr.Dataset(
            {"xco2": (["retrieval"], xco2)},
            coords={
                "time": ("retrieval", retrieval_time),
                "lat": ("retrieval", retrieval_lat),
                "lon": ("retrieval", retrieval_lon),
            },
        )
