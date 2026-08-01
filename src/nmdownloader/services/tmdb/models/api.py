from typing import Any

import requests

from nmdownloader.config import app_settings


class TMDBApi:
    TIMEOUT = 10
    BASE_URL = app_settings.tmdb.api_url
    API_KEY = app_settings.tmdb.api_key
    API_VERSION = app_settings.tmdb.api_version

    @classmethod
    def _call(cls, endpoint: str, **kwargs) -> dict[str, Any]:
        url = f"{cls.BASE_URL}/{cls.API_VERSION}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.request(url=url, headers=headers, timeout=cls.TIMEOUT, **kwargs)
        response.raise_for_status()
        response_json = response.json()

        return response_json

    @classmethod
    def search_movie(cls, query: str) -> dict[str, Any]:
        return cls._call(method="GET", endpoint="search/movie", params={"page": "1", "query": query})

    @classmethod
    def get_thumbnail(cls, query: str) -> str | None:
        response = cls.search_movie(query=query)
        results = response.get("results")
        if not isinstance(results, list) or not results:
            return None
        if not (poster_path := results[0].get("poster_path")):
            return None

        return poster_path
