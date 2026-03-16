import requests
from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.services.download_media import DownloadMedia


class Download1fichier(DownloadMedia):
    def __init__(self, url: str, **kwargs) -> None:
        super().__init__(url=compute_url_from_1fichier(link=url), **kwargs)


def compute_url_from_1fichier(link: str):
    url, *_ = link.split("&")
    token_response = requests.post(
        url=f"{app_settings.download.un_fichier_api_url}/download/get_token.cgi",
        json={"url": url},
        headers={"Authorization": f"Bearer {app_settings.download.un_fichier_token}"},
        timeout=10,
    )
    token_response.raise_for_status()

    download_dct = token_response.json()
    ready_url = download_dct.get("url")
    logger.info(f"Ready to download: {ready_url}")

    return ready_url
