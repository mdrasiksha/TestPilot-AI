from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TestPilot AI Backend"
    app_env: str = Field(default="development", alias="APP_ENV")
    api_prefix: str = "/api/v1"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    openai_api_key: str = ""
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
