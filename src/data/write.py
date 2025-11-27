from typing import Literal

import pandas as pd
from src.config import DATA_DIR, TEMPANOMALIES, CO2, settings


def _write_csv(df: pd.DataFrame, filename: str, locally: bool = True):
    if locally:
        path = DATA_DIR / "processed" / f"{filename}.csv"
        df.to_csv(path, sep="\t", encoding="utf-8", index=False, header=True)
    else:
        _write_to_s3(df, filename, format="csv")


def _write_parquet(df: pd.DataFrame, filename: str, locally: bool = True):
    if locally:
        path = DATA_DIR / "processed" / f"{filename}.parquet"
        df.to_parquet(path, index=False)
    else:
        _write_to_s3(df, filename, format="csv")


def _write_to_s3(
    df: pd.DataFrame, filename: str, format: Literal["csv", "parquet"] = "parquet"
):
    if not settings.S3_BUCKET and not settings.AWS_KEY and not settings.AWS_SECRET:
        raise ValueError(
            "S3_BUCKET, AWS_KEY, and AWS_SECRET must be set in order to upload to S3."
        )
    storage_options = {
        "key": settings.AWS_KEY,
        "secret": settings.AWS_SECRET,
    }
    s3_path = f"s3://{settings.S3_BUCKET}/processed/{filename}.{format}"
    if format == "parquet":
        df.to_parquet(
            s3_path,
            storage_options=storage_options,
            index=False,
        )
    elif format == "csv":
        df.to_csv(
            s3_path,
            storage_options=storage_options,
            index=False,
        )


def write_tempanomalies(df: pd.DataFrame, locally: bool = True):
    _write_parquet(df, TEMPANOMALIES, locally)


def write_co2(df: pd.DataFrame, locally: bool = True):
    _write_parquet(df, CO2, locally)
