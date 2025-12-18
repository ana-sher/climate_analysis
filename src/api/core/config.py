import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR = ROOT / 'outputs' / 'plots'
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
CO2 = 'co2'
TEMPANOMALIES = 'tempanomalies'
DOTENV = ROOT / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_ignore_empty=True,
        extra="ignore",
    )
    S3_BUCKET: str | None = None
    EARTHDATA_USERNAME: str = ""
    EARTHDATA_PASSWORD: str = ""
    AAA: str = ""


settings = Settings()
