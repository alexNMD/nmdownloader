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
    api_version: str = "3"
    api_key: str | None = None

    image_url: str = "https://image.tmdb.org"
    poster_width: Literal["200", "300", "400", "500"] = "200"
    languages_iso639_1: list[str] = ["fr", "en"]
