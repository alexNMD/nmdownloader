from services.download.models.media import DownloadMedia


class DownloadDefault(DownloadMedia):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
