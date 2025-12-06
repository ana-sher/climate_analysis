from typing import Optional

import pandas as pd
import numpy as np

from sklearn import ensemble
from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

import mlflow
import mlflow.sklearn as mls


def train_model(df: pd.DataFrame,
                features: Optional[list[str]] = None, target: str = "tempanomaly", epochs=10) -> BaseEstimator:
    """
    Trains the given model on the provided data and labels for a specified number of epochs.

    Parameters:
    df: The input DataFrame for training.
    features: The features for training.
    target: The target variable for training.
    epochs: The number of epochs to train the model.

    Returns:
    model: The trained model.
    """
    if features is None:
        features = ["lat", "lon", "month_sin", "month_cos", "year", "co2", "land_cover_type",
                    "land_cover_type_year"]
    _validate_train_input(df, features, target, epochs)

    mlflow.set_experiment("Tempanomaly Prediction", experiment_id='1')

    with mlflow.start_run():
        X = np.array(
            df[*features])
        y = np.array(df[target])
        mls.autolog()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )

        model = _prediction_model()
        for epoch in range(epochs):
            model.fit(X_train, y_train)

        score: float = model.score(X_test, y_test)
        mse = mean_squared_error(y_test, model.predict(X_test))

        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2", score)

        mlflow.log_params(model.get_params())

        mls.log_model(sk_model=model, name="gradient_boosting_model", input_example=X_train[:5])
    return model


def _load_model(run_id: str, model_name: str = "gradient_boosting_model") -> BaseEstimator:
    """
    Loads a trained model from MLflow using the given run ID.

    Parameters:
    run_id: The MLflow run ID where the model is stored.
    model_name: The name of the model to load.

    Returns:
    model: The loaded trained model.
    """
    model_uri = f"runs:/{run_id}/{model_name}"
    model = mls.load_model(model_uri=model_uri)
    return model

def load_latest_model(model_name: str = "gradient_boosting_model") -> BaseEstimator:
    """
    Loads the latest trained model from MLflow.

    Parameters:
    model_name: The name of the model to load.

    Returns:
    model: The loaded trained model.
    """
    mlflow.set_experiment("Tempanomaly Prediction", experiment_id='1')
    client = mlflow.tracking.MlflowClient()
    experiments = client.get_experiment_by_name("Tempanomaly Prediction")
    runs = client.search_runs(
        experiment_ids=[experiments.experiment_id],
        filter_string="",
        order_by=["attributes.start_time DESC"],
        max_results=1,
    )
    if not runs:
        raise ValueError("No runs found in the experiment.")
    latest_run = runs[0]
    return _load_model(run_id=latest_run.info.run_id, model_name=model_name)


def _prediction_model() -> BaseEstimator:
    """
    Creates and returns a chosen prediction model with predefined parameters.

    Returns:
    model: Prediction model.
    """
    params = {
        "n_estimators": 800,
        "max_depth": 4,
        "min_samples_split": 10,
        "learning_rate": 0.01,
        "loss": "huber",
        "max_features": "sqrt",
        "random_state": 42,
    }
    return ensemble.GradientBoostingRegressor(**params)


def _validate_train_input(df: pd.DataFrame, features: list[str], target: str, epochs: int):
    """
    Validates the input for training.

    Parameters:
    df: The input DataFrame to validate.
    features: The features for training.
    target: The target variable for training.
    epochs: The number of epochs to train the model.

    Raises:
    ValueError: If any validation check fails.
    """
    if df is None:
        raise ValueError("Input DataFrame cannot be None.")
    if features is None:
        raise ValueError("Features list cannot be None.")
    if target in features:
        raise ValueError("Target variable cannot be one of the features.")
    if target not in df.columns:
        raise ValueError(f"Target variable '{target}' not found in DataFrame columns.")
    if epochs <= 0:
        raise ValueError("Number of epochs must be a positive integer.")
