from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class TMDBConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TMDB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    api_url: str = "https://api.themoviedb.org"
    image_url: str = "https://image.tmdb.org"
    api_version: str = "3"
    poster_width: Literal["200", "300", "400", "500"] = "200"
    api_key: str | None = None
