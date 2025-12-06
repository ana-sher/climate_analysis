from datetime import timedelta
import numpy as np
from pandas import DataFrame
import pandas as pd


def extract_features(t_df: pd.DataFrame, co2_df: pd.DataFrame, land_cover_df: pd.DataFrame,
                     lat_range: float = 0.01, lon_range: float = 0.02) -> pd.DataFrame:
    """
    Extracts features from CO2, temperature anomalies and land cover types DataFrames.

    Parameters:
        t_df: DataFrame containing tempanomaly (K) by lat, lon, time
        co2_df: DataFrame containing xco2 (ppm) by lat, lon, time
        land_cover_df: DataFrame containing land cover types by lat, lon, time
        lat_range: float: range precision of latitude coordinates to align with tempanomalies data
        lon_range: float: range precision of longitude coordinates to align with tempanomalies data
    Returns:
        pd.DataFrame: DataFrame with extracted features
    """
    t_df = _extract_tempanomaly_features(t_df)

    def _align_coordinates(df: pd.DataFrame, row: pd.Series) -> pd.Series[bool]:
        """Aligns coordinates of a DataFrame row within specified lat/lon ranges."""
        return ((df["lat"] + lat_range) >= row["lat"]) & ((df["lat"] - lat_range) <= row["lat"]) & (
                (df["lon"] + lon_range) >= row["lon"]) & ((df["lon"] - lon_range) <= row["lon"])

    co2_rows_candidates: list[DataFrame] = [
        co2_df[_align_coordinates(co2_df, row)]
        .assign(delta=co2_df["lat"] - row["lat"] + co2_df["lon"] - row["lon"])
        .sort_values("delta", ascending=True)
        for _, row in t_df.iterrows()
    ]

    t_df["co2"] = [
        (row.iloc[0]["xco2"] if row.size > 0 else None)
        for _, row in enumerate(co2_rows_candidates)
    ]
    t_df.dropna(inplace=True)

    land_types_rows_candidates: list[DataFrame] = [
        land_cover_df[_align_coordinates(land_cover_df, row)
                      & (((land_cover_df["time"] + 1) == row["year"]) | ((land_cover_df["time"]) == row["year"]))
                      ]
        .assign(delta=co2_df["lat"] - row["lat"] + co2_df["lon"] - row["lon"])
        .sort_values("delta", ascending=True)
        for _, row in t_df.iterrows()
    ]
    t_df["land_cover_type"] = [
        row.iloc[0]["land_cover_type"] if row.size > 0 else None
        for row in land_types_rows_candidates
    ]
    t_df["land_cover_type_year"] = [
        row.iloc[0]["time"] if row.size > 0 else None
        for row in land_types_rows_candidates
    ]
    t_df.dropna(inplace=True)
    return t_df


def _extract_tempanomaly_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts features from temperature anomalies DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing tempanomaly (K) by lat, lon, time
    Returns:
        pd.DataFrame: DataFrame with extracted features
    """
    t_df = df.dropna(inplace=False).copy()

    t_df["month"] = list(map(lambda t: t.to_pydatetime().month, t_df["time"]))
    t_df["season"] = list(map(lambda t: ((t % 12) // 3) + 1, t_df["month"]))
    t_df["year"] = list(map(lambda t: t.to_pydatetime().year, t_df["time"]))
    t_df["month_sin"] = np.sin(2 * np.pi * t_df["month"] / 12)
    t_df["month_cos"] = np.cos(2 * np.pi * t_df["month"] / 12)
    t_df["time"] = list(map(lambda t: t.timestamp(), t_df["time"]))

    return t_df
