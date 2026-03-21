import requests
from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.libs.download import DownloadException
from nmdownloader.libs.plugins import register_downloader
from nmdownloader.services.download_media import DownloadMedia


@register_downloader("1fichier.com")
class Download1fichier(DownloadMedia):
    def __init__(self, url: str, **kwargs) -> None:
        if not (bearer_token := app_settings.downloader.un_fichier_token):
            raise DownloadException(self, "DOWNLOAD_UN_FICHIER_TOKEN not set")

        try:
            download_1fichier_url = compute_url_from_1fichier(
                link=url, token=bearer_token
            )
        except Exception as error:
            raise DownloadException(self, str(error)) from error

        super().__init__(url=download_1fichier_url, **kwargs)


def compute_url_from_1fichier(link: str, token: str) -> str:
    url, *_ = link.split("&")
    token_response = requests.post(
        url=f"{app_settings.downloader.un_fichier_api_url}/download/get_token.cgi",
        json={"url": url},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    token_response.raise_for_status()

    download_dct = token_response.json()
    ready_url = download_dct.get("url")
    logger.info(f"Ready to download: {ready_url}")

    return ready_url
