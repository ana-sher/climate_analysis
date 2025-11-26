from pathlib import Path
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
    AWS_KEY: str | None = None
    AWS_SECRET: str | None = None
    S3_BUCKET: str | None = None
    EARTHDATA_USERNAME: str = ""
    EARTHDATA_PASSWORD: str = ""

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("EARTHDATA_USERNAME", self.EARTHDATA_USERNAME)
        self._check_default_secret("EARTHDATA_PASSWORD", self.EARTHDATA_PASSWORD)

        return self

settings = Settings()