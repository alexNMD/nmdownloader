from nmdownloader.services.download.helpers.exceptions import DownloadError
from nmdownloader.services.download.helpers.plugins import register_downloader
from nmdownloader.services.download.models import DownloadMedia
from nmdownloader.services.notification import UnFichierAPI


@register_downloader("1fichier.com")
class Download1fichier(DownloadMedia):
    def __init__(self, url: str, **kwargs) -> None:
        try:
            url_to_compute, *_ = url.split("&")
            download_1fichier_url = UnFichierAPI.compute_url(url=url_to_compute)
        except Exception as error:
            raise DownloadError(self, str(error)) from error

        if not download_1fichier_url:
            raise DownloadError(self, "Unable to get download url")

        super().__init__(url=download_1fichier_url, **kwargs)
