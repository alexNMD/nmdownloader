from typing import Any

from nmdownloader.config import app_settings

from ..models.base import BaseNotification


class TMDBApi(BaseNotification):
    BASE_URL = app_settings.tmdb.api_url
    IMAGE_URL = app_settings.tmdb.image_url
    API_KEY = app_settings.tmdb.api_key
    API_VERSION = app_settings.tmdb.api_version
    POSTER_WIDTH = app_settings.tmdb.poster_width

    @classmethod
    def get_results(cls, **kwargs) -> list[dict[str, Any]] | None:
        headers = {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json",
        }
        response_json = cls._call_and_get_json(method="GET", headers=headers, **kwargs)
        results = response_json.get("results")

        if not isinstance(results, list) or not results:
            return None

        return results

    @classmethod
    def get_thumbnail(cls, query: str) -> str | None:
        params = {"page": "1", "include_adult": True, "query": query}
        if not (results := cls.get_results(endpoint="search/multi", params=params)):
            return None

        if not (poster_path := results[0].get("poster_path")):
            return None

        return f"{cls.IMAGE_URL}/t/p/w{cls.POSTER_WIDTH}{poster_path}"
