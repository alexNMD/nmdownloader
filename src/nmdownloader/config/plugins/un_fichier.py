from pydantic_settings import BaseSettings, SettingsConfigDict


class UnFichierDownloaderConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="UNFICHIER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    api_url: str = "https://api.1fichier.com"
    api_version: str = "v1"
    api_token: str | None = None
