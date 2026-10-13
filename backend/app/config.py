from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    database_path: Path = BACKEND_DIR / "data" / "dash-vps.db"
    ingest_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DASH_VPS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
