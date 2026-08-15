from typing import Any

from nmdownloader.config import app_settings

from ..models.base import BaseNotification


class TMDBApi(BaseNotification):
    BASE_URL = app_settings.tmdb.api_url
    API_VERSION = app_settings.tmdb.api_version
    API_TOKEN = app_settings.tmdb.api_key
    IMAGE_URL = app_settings.tmdb.image_url
    POSTER_WIDTH = app_settings.tmdb.poster_width

    @classmethod
    def get_results(cls, **kwargs) -> list[dict[str, Any]] | None:
        response_json = cls._call_and_get_json(method="GET", **kwargs)
        results = response_json.get("results")

        if not isinstance(results, list) or not results:
            return None

        return results

    @classmethod
    def get_thumbnail(cls, query: str) -> str | None:
        _default_params = {"page": "1", "include_adult": True, "query": query}
        results = []
        # TODO: refacto when python3.15 release (unpacking in list comprehension)
        for language in app_settings.tmdb.languages_iso639_1:
            params = {**_default_params, **{"language": language}}
            if result := cls.get_results(endpoint="search/multi", params=params):
                results.extend(result)

        if not (most_popular := max(results, key=lambda x: x.get("popularity", 0), default=None)):
            return None

        if not (poster_path := most_popular.get("poster_path")):
            return None

        return f"{cls.IMAGE_URL}/t/p/w{cls.POSTER_WIDTH}{poster_path}"
