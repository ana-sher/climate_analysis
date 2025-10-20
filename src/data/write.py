import pandas as pd
import xarray as xr
from pathlib import Path

from config import DATA_DIR, TEMPANOMALIES_CSV, CO2_CSV

def _write_csv(df: pd.DataFrame, filename: str):
    path = DATA_DIR / 'processed' / filename
    return df.to_csv(path, sep='\t', encoding='utf-8', index=False, header=True)

def write_tempanomalies(df: pd.DataFrame):
    return _write_csv(df, TEMPANOMALIES_CSV)

def write_co2(df: pd.DataFrame):
    return _write_csv(df, CO2_CSV)