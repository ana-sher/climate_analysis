from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np

from sklearn.base import BaseEstimator


def predict(model: BaseEstimator, df: pd.DataFrame, features: Optional[list[str]] = None) -> np.ndarray:
    """
    Makes predictions using the trained model on the provided DataFrame.

    Parameters:
    model: The trained model.
    df: The input DataFrame for making predictions.
    features: The features for making predictions.

    Returns:
    predictions: The predicted values as a numpy array.
    """
    if df is None:
        raise ValueError("Input DataFrame cannot be None.")
    if features is None:
        features = ["lat", "lon", "month_sin", "month_cos", "year", "co2", "land_cover_type",
                    "land_cover_type_year"]
    X = np.array(df[*features])
    predictions = model.predict(X)
    return predictions


def predict_for_region(
        model: BaseEstimator,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        date_from: datetime,
        date_to: datetime,
) -> pd.DataFrame:
    """
    Makes predictions for a specified region and time range.

    Parameters:
    model: The trained model.
    lat_min, lat_max, lon_min, lon_max: The bounding box coordinates.
    date_from, date_to: The time range for predictions.

    Returns:
    predictions_df: A DataFrame containing the predictions.
    """
    latitudes = np.arange(lat_min, lat_max, 1.0)
    longitudes = np.arange(lon_min, lon_max, 1.0)
    times = pd.date_range(start=date_from, end=date_to, freq='M')

    data = []
    for time in times:
        month = time.month
        year = time.year
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        for lat in latitudes:
            for lon in longitudes:
                data.append({
                    "lat": lat,
                    "lon": lon,
                    "month": month,
                    "year": year,
                    "month_sin": month_sin,
                    "month_cos": month_cos,
                    "co2": 415.0,  # Placeholder value; replace with actual data retrieval
                    "land_cover_type": 1,  # Placeholder value; replace with actual data retrieval
                    "land_cover_type_year": year,
                })

    df = pd.DataFrame(data)
    df['predicted_tempanomaly'] = predict(model, df)

    return df
