import pandas as pd

from config import DATA_DIR, TEMPANOMALIES, CO2

def _write_csv(df: pd.DataFrame, filename: str):
    path = DATA_DIR / 'processed' / f'{filename}.csv'
    return df.to_csv(path, sep='\t', encoding='utf-8', index=False, header=True)

def _write_parquet(df: pd.DataFrame, filename: str):
    path = DATA_DIR / 'processed' / f'{filename}.parquet'
    return df.to_parquet(path, index=False)

def write_tempanomalies(df: pd.DataFrame):
    return _write_parquet(df, TEMPANOMALIES)

def write_co2(df: pd.DataFrame):
    return _write_parquet(df, CO2)