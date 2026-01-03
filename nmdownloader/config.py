from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# DISCORD_TOKEN = os.getenv("DOWNLOAD_DISCORD_TOKEN")
# DOWNLOAD_TOKEN = os.getenv("DOWNLOAD_TOKEN")
# BOT_MESSAGES_CHANNEL_ID = int(os.getenv("BOT_MESSAGES_CHANNEL_ID"))
# NAS_PATH = os.getenv("DOWNLOAD_PATH")
# REFRESH_RATE = int(os.getenv("REFRESH_RATE", default="10"))  # Default => 10 seconds
# LIMIT = int(os.getenv("CONCURRENCY", default="4"))  # Default => 4 threads
# LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO")
# CHUNK_SIZE = 1024 * 64  # 64 KB

# PREFIX = "!"
# ADMINS = (
#     [admin.strip() for admin in os.getenv("DISCORD_ADMINS").split(",")]
#     if os.getenv("DISCORD_ADMINS")
#     else []
# )

## LOGGER settings
# logger = logging.getLogger(__name__)
# logging.basicConfig(
#     level=LOG_LEVEL, format="[{asctime}] [{levelname}] : {message}", style="{"
# )
# gunicorn_logger = logging.getLogger("gunicorn.error")
# gunicorn_logger.setLevel(LOG_LEVEL)
#
# BROKER_URL = os.getenv("BROKER_URL")
# BACKEND_URL = os.getenv("BACKEND_URL")

# BASE_URL_1FICHIER = "https://api.1fichier.com/v1"
# BASE_URL_DISCORD = "https://discord.com/api/v10"


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
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )

    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    celery: CeleryConfig = Field(default_factory=CeleryConfig)
    download: DownloadConfig = Field(default_factory=DownloadConfig)

    log_level: str = Field(default="INFO")
    media_path: Path = Field(default=Path("/media"))


@lru_cache
def get_app_settings():
    return Settings()


app_settings = get_app_settings()
