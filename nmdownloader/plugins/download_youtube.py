from pathlib import Path

from pytubefix import YouTube  # type: ignore
from loguru import logger
from werkzeug.utils import secure_filename

from nmdownloader.config import app_settings
from nmdownloader.libs.download import DownloadStatus, DownloadException
from nmdownloader.services.download import Download


class DownloadYoutube(Download):
    def __init__(self, url: str, **kwargs) -> None:
        self.youtube_obj = YouTube(url=url)
        self.filename = secure_filename(
            str(Path(self.youtube_obj.title).with_suffix(".mp4"))
        )
        self.base_download_path: Path = app_settings.media_path / "youtube"

        super().__init__(filepath=(self.base_download_path / self.filename), **kwargs)

    def start(self):
        try:
            self.update_status(DownloadStatus.STARTED)
            self.base_download_path.mkdir(parents=True, exist_ok=True)
            video_stream = self.youtube_obj.streams.get_highest_resolution()
            self.update_status(DownloadStatus.RUNNING)
            logger.info(f"Youtube Download: {self.filename}")
            video_stream.download(
                output_path=str(self.base_download_path), filename=str(self.filename)
            )

            ### Finish
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
