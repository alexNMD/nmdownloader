from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        default="ultrafast",
        pattern="^(ultrafast|superfast|veryfast|faster|fast|medium|slow|slower|veryslow)$",
    )
    profile_v: str = Field(default="baseline", alias="profile:v")
    tune: str = "fastdecode"
    acodec: str = "aac"
    audio_bitrate: str = Field(default="96k", alias="b:a")
    movflags: str = "+faststart"
    format: str = "mp4"


class YoutubeDownloaderConfig(BaseSettings):
    ffmpeg: FFMPEGVideoConfig = Field(default_factory=FFMPEGVideoConfig)
