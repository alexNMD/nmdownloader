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
    default_channel_id: int
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


class FFMPEGVideoConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FFMPEG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    vcodec: str = "libx264"
    crf: int = Field(default=30, ge=0, le=51)
    preset: str = Field(
        default="fast",
        pattern="^(ultrafast|superfast|veryfast|faster|fast|medium|slow|slower|veryslow)$",
    )
    profile_v: str = Field(default="baseline", alias="profile:v")
    acodec: str = "aac"
    audio_bitrate: str = Field(default="96k", alias="b:a")
    movflags: str = "+faststart"
    format: str = "mp4"

    def to_dict(self) -> dict:
        return {
            "vcodec": self.vcodec,
            "crf": self.crf,
            "preset": self.preset,
            "profile:v": self.profile_v,
            "acodec": self.acodec,
            "b:a": self.audio_bitrate,
            "movflags": self.movflags,
            "format": self.format,
        }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    celery: CeleryConfig = Field(default_factory=CeleryConfig)
    download: DownloadConfig = Field(default_factory=DownloadConfig)
    ffmpeg: FFMPEGVideoConfig = Field(default_factory=FFMPEGVideoConfig)

    media_path: Path = Field(default=Path("/media"))
    nmd_log_level: str = Field(default="INFO")


@lru_cache
def get_app_settings() -> Settings:
    return Settings()


app_settings = get_app_settings()
