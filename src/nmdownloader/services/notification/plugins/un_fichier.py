from nmdownloader.config import app_settings

from ..models.base import BaseNotification


class UnFichierAPI(BaseNotification):
    BASE_URL = app_settings.downloader.un_fichier.api_url
    API_VERSION = app_settings.downloader.un_fichier.api_version
    API_TOKEN = app_settings.downloader.un_fichier.api_token

    @classmethod
    def compute_url(cls, url: str) -> str | None:
        response_json = cls._call_and_get_json(method="POST", endpoint="download/get_token.cgi", json={"url": url})

        return response_json.get("url")
