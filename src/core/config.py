from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR = Path(__file__).resolve().parents[1] / 'outputs' / 'plots'
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
CO2 = 'co2'
TEMPANOMALIES = 'tempanomalies'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    S3_BUCKET: str | None = None
    EARTHDATA_USERNAME: str = ""
    EARTHDATA_PASSWORD: str = ""


settings = Settings()
