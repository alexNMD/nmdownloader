from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DiscordConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DISCORD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    token: str
    default_channel_id: str
    command_prefix: str = "!"
    admins: list[str] = Field(default_factory=list)
    refresh_rate: int = Field(default=10)
    api_url: str = "https://discord.com/api/v10"


class CeleryConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CELERY_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    concurrency: int = Field(default=5)
    broker_url: str = Field(default="redis://redis:6379/0")
    backend_url: str = Field(default="redis://redis:6379/0")


class DownloadConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DOWNLOAD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    un_fichier_token: str
    un_fichier_api_url: str = "https://api.1fichier.com/v1"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    celery: CeleryConfig = Field(default_factory=CeleryConfig)
    download: DownloadConfig = Field(default_factory=DownloadConfig)

    media_path: Path = Field(default=Path("/media"))
    nmd_log_level: str = Field(default="INFO")


@lru_cache
def get_app_settings():
    return Settings()


app_settings = get_app_settings()
