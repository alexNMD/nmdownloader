from nmdownloader.services.download.models.media import DownloadMedia


class DownloadDefault(DownloadMedia):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def download_url(self) -> str:
        return self.url
