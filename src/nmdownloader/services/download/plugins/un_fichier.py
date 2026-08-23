from functools import cached_property

from nmdownloader.services.download.helpers.exceptions import DownloadError
from nmdownloader.services.download.helpers.plugins import register_downloader
from nmdownloader.services.download.models import DownloadMedia
from nmdownloader.services.notification import UnFichierAPI


@register_downloader("1fichier.com")
class Download1fichier(DownloadMedia):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @cached_property
    def download_url(self) -> str:
        try:
            _url_to_compute, *_ = self.url.split("&")
            if not (download_1fichier_url := UnFichierAPI.compute_url(url=_url_to_compute)):
                raise DownloadError(self, "Unable to get download url")
            return download_1fichier_url
        except Exception as error:
            raise DownloadError(self, str(error)) from error
