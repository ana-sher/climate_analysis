from functools import singledispatch
from typing import Literal, Union
import zarr

import pandas as pd
import xarray as xr
from src.config import DATA_DIR, TEMPANOMALIES, CO2, settings

def _write_csv(df: pd.DataFrame, filename: str, locally: bool = True, bucket: str = ""):
    path = DATA_DIR / "processed" / f"{filename}.csv" if locally else _get_s3_path(filename, "csv", bucket)
    df.to_csv(path, sep="\t", encoding="utf-8", index=False, header=True)


def _write_parquet(df: pd.DataFrame, filename: str, locally: bool = True, bucket: str = ""):
    path = DATA_DIR / "processed" / f"{filename}.parquet" if locally else _get_s3_path(filename, "parquet", bucket)
    df.to_parquet(path, index=False)


def _write_zarr(data: Union[xr.Dataset, pd.DataFrame], filename: str, locally: bool = True, bucket: str = ""):
    path = DATA_DIR / "processed" / f"{filename}.zarr" if locally else _get_s3_path(filename, "zarr", bucket)

    store = zarr.DirectoryStore(path)
    ds = data if type(data) is xr.Dataset else data.to_xarray()

    chunks = auto_chunk(ds)
    ds = ds.chunk(chunks)
    ds.to_zarr(store, mode="w")


def _get_s3_path(filename: str, data_format: Literal["csv", "parquet", "zarr"] = "zarr", bucket: str= "") -> str:
    if not settings.S3_BUCKET and not bucket:
        raise ValueError(
            "S3_BUCKET must be set in order to upload to S3."
        )
    s3_bucket = bucket if bucket else settings.S3_BUCKET
    s3_path = f"s3://{s3_bucket}/processed/{filename}.{data_format}"
    return s3_path


def auto_chunk(ds: xr.Dataset, target_mb: int = 5) -> dict[str, int]:
    target_bytes = target_mb * 1024 * 1024
    chunks = {}

    largest_var = max(ds.data_vars, key=lambda v: ds[v].nbytes)
    itemsize = ds[largest_var].dtype.itemsize

    dims = ds[largest_var].dims
    chunk_sizes = list([ds.sizes[d] for d in dims])

    while True:
        est = itemsize
        for s in chunk_sizes:
            est *= s
        if est <= target_bytes:
            break

        largest_dim_index = chunk_sizes.index(max(chunk_sizes))
        chunk_sizes[largest_dim_index] = max(1, chunk_sizes[largest_dim_index] // 2)

    for dim, val in zip(dims, chunk_sizes):
        chunks[dim] = val

    return chunks


def write_tempanomalies(df: pd.DataFrame, locally: bool = True):
    _write_zarr(df, TEMPANOMALIES, locally)


def write_co2(data: Union[xr.Dataset, pd.DataFrame], locally: bool = True, bucket: str = "climate-analysis-bucket"):
    _write_zarr(data, CO2, locally, bucket)
