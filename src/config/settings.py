from functools import lru_cache
from importlib.metadata import version
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.plugins.discord import DiscordConfig
from config.plugins.un_fichier import UnFichierDownloaderConfig
from config.plugins.youtube import YoutubeDownloaderConfig


class CeleryConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CELERY_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    concurrency: int = Field(default=5)
    broker_url: str = Field(default="redis://redis:6379/0")
    backend_url: str = Field(default="redis://redis:6379/0")


class DownloaderPluginConfig(BaseSettings):
    modules: list[str] = ["un_fichier.Download1fichier", "youtube.DownloadYoutube"]
    registry: dict[str, type] = {}


class DownloaderConfig(BaseSettings):
    plugin: DownloaderPluginConfig = Field(default_factory=DownloaderPluginConfig)

    un_fichier: UnFichierDownloaderConfig = Field(
        default_factory=UnFichierDownloaderConfig
    )
    youtube: YoutubeDownloaderConfig = Field(default_factory=YoutubeDownloaderConfig)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    celery: CeleryConfig = Field(default_factory=CeleryConfig)
    downloader: DownloaderConfig = Field(default_factory=DownloaderConfig)

    media_path: Path = Field(default=Path("/media"))
    nmd_log_level: str = Field(default="INFO")
    version: str = version("nmdownloader")


@lru_cache
def get_app_settings() -> Settings:
    return Settings()
