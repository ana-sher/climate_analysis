import pandas as pd
import xarray as xr
from pathlib import Path
from typing import Literal, Optional
import h5py

from config import DATA_DIR, TEMPANOMALIES_CSV, CO2_CSV


def load_co2() -> pd.DataFrame:
    return _load_csv(CO2_CSV)


def load_tempanomalies() -> pd.DataFrame:
    return _load_csv(TEMPANOMALIES_CSV)


def read_raw_tempanomalies(year_from: int, lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> pd.DataFrame:
    # source: GISTEMP, NASA http://data.giss.nasa.gov/gistemp/
    # dims: time, nv, lat, lon
    # vars: time_bnds, tempanomaly (K)
    temp_anomalies_ds = _get_raw_filenames_dataset('nc', prefix='gistemp')

    temp_anomalies_ds = temp_anomalies_ds.sel(
        time=temp_anomalies_ds['time'].dt.year >= year_from)
    temp_anomalies_ds = temp_anomalies_ds.sel(lat=slice(lat_min, lat_max),
                                              lon=slice(lon_min, lon_max))
    # temp_anomalies_ds = temp_anomalies_ds.dropna(
    #     dim='time', subset=['tempanomaly'])

    temp_anomalies_df = temp_anomalies_ds['tempanomaly'].to_dataframe(
    ).reset_index()
    # df structure: tempanomaly by lat, lon, time
    return temp_anomalies_df


def read_raw_co2(year_from: int, lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> pd.DataFrame:
    # source: GES DISC, NASA L2 data https://disc.gsfc.nasa.gov/datasets/OCO2_L2_Standard_11r/summary
    # initial group structure, getting measurements from RetrievalResults group and dims from RetrievalGeometry, RetrievalHeader
    # dims: retrieval (artificially created)
    # vars: xco2 (ppm)
    # coords: time, lat, lon
    path = DATA_DIR / 'raw'
    files = list(Path(path).glob(f'oco*.h5'))
    if not files:
        raise FileNotFoundError('No files found for co2 reading')
    datasets = [_get_oco_file_ds(path / file.name)
                for file in files]

    if len(datasets) == 1:
        return datasets[0]['xco2'].to_dataframe(
        ).reset_index()
    combined = xr.concat(datasets, dim='retrieval')
    combined = combined.assign_coords(time=('retrieval', pd.to_datetime(
        combined['time'].values, utc=True).tz_localize(None)))

    co2_ds = combined.where(
        combined['time'].dt.year >= year_from, drop=True)
    co2_ds = co2_ds.where((co2_ds['lat'] >= lat_min) & (co2_ds['lat'] <= lat_max) & (co2_ds['lon'] >= lon_min) & (co2_ds['lon'] <= lon_max),
                          drop=True)

    co2_df = co2_ds['xco2'].to_dataframe(
    ).reset_index()
    # df structure: xco2 by lat, lon, time
    return co2_df


def _load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / 'processed' / filename
    return pd.read_csv(path)


def _load_netcdf(filename: str, engine: Optional[str] = None) -> xr.Dataset:
    path = DATA_DIR / 'raw' / filename
    return xr.open_dataset(path, engine=engine)


def _get_raw_filenames_dataset(file_format: Literal['h5', 'nc'], concat_dim: str = 'time', prefix: str = '') -> xr.Dataset:
    path = DATA_DIR / 'raw'
    if file_format == 'h5':
        engine = 'h5netcdf'
    elif file_format == 'nc':
        engine = 'netcdf4'
    files = list(Path(path).glob(f'{prefix}*.{file_format}'))
    if not files:
        raise FileNotFoundError('No files found matching the pattern')
    datasets = [_load_netcdf(file.name, engine) for file in files]
    if len(datasets) == 1:
        return datasets[0]
    combined = xr.concat(datasets, dim=concat_dim)
    return combined


def _get_oco_file_ds(path: Path) -> xr.Dataset:
    with h5py.File(path, 'r') as f:
        retrieval_lat = f['RetrievalGeometry/retrieval_latitude'][:]
        retrieval_lon = f['RetrievalGeometry/retrieval_longitude'][:]
        retrieval_time = [time.decode(
            'utf-8') for time in f['RetrievalHeader/retrieval_time_string'][:]]

        xco2 = [x * 1e6 for x in f['RetrievalResults/xco2'][:]]
        return xr.Dataset(
            {
                'xco2': (['retrieval'], xco2)
            },
            coords={
                'time': ('retrieval', retrieval_time),
                'lat': ('retrieval', retrieval_lat),
                'lon': ('retrieval', retrieval_lon)
            }
        )
