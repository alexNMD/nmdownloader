from pathlib import Path

from pytubefix import YouTube

from nmdownloader.config import app_settings
from nmdownloader.libs.download import DownloadStatus, DownloadException
from nmdownloader.services.download import Download


class DownloadYoutube(Download):
    def __init__(self, url: str, **kwargs) -> None:
        self.url = self._compute_url(url)
        self.youtube_obj = YouTube(url=url)
        self.filename = str(Path(self.youtube_obj.title).with_suffix(".mp4"))
        self.type_dl = "youtube"
        self.base_download_path: Path = app_settings.media_path / self.type_dl
        self.filepath = self.base_download_path / self.filename
        self.finished = False

        super().__init__(type_dl=self.type_dl, filepath=self.filepath, **kwargs)

    def start(self):
        try:
            self.update_status(DownloadStatus.STARTED)
            self.base_download_path.mkdir(parents=True, exist_ok=True)
            video_stream = self.youtube_obj.streams.get_highest_resolution()
            self.update_status(DownloadStatus.RUNNING)
            video_stream.download(
                output_path=str(self.base_download_path), filename=str(self.filename)
            )

            ### Finish
            self.finished = True
            self.update_status(DownloadStatus.DONE)
        except (
            FileNotFoundError,
            NotImplementedError,
            ValueError,
        ) as error:
            raise DownloadException(self, error) from error
        except Exception as error:
            self._remove()
            raise DownloadException(self, error) from error
