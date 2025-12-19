from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file="src\.env",
        extra="ignore",
    )

Config = Settings()