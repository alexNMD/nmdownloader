from pathlib import Path

import ffmpeg
from loguru import logger
from pytubefix import YouTube
from werkzeug.utils import secure_filename

from nmdownloader.config import app_settings
from nmdownloader.services.download.helpers import DownloadStatus
from nmdownloader.services.download.helpers.exceptions import DownloadError
from nmdownloader.services.download.helpers.plugins import register_downloader
from nmdownloader.services.download.models import DownloadBase


@register_downloader("www.youtube.com", "youtube.com", "youtu.be")
class DownloadYoutube(DownloadBase):
    def __init__(self, url: str, **kwargs) -> None:
        self.youtube_obj = YouTube(url=url)
        self.filename = secure_filename(str(Path(self.youtube_obj.title).with_suffix(".mp4")))
        self.base_download_path: Path = app_settings.media_path / "youtube"
        self.video_path: str | None = None
        self.audio_path: str | None = None

        super().__init__(filepath=(self.base_download_path / self.filename), **kwargs)

    @property
    def thumbnail(self) -> str:
        return self.youtube_obj.thumbnail_url

    def _setup(self) -> None:
        self.update_status(DownloadStatus.STARTED)
        self.base_download_path.mkdir(parents=True, exist_ok=True)

    def _terminate(self) -> None:
        self._multiplexage()
        self.update_status(DownloadStatus.DONE)

    def _download(self) -> None:
        try:
            logger.info(f"Youtube Download: {self.filename}")
            video_stream = self.youtube_obj.streams.get_highest_resolution(progressive=False)

            if not video_stream:
                raise AttributeError(f"No video stream found for {self.youtube_obj.title}")
            if not (audio_streams := self.youtube_obj.streams.get_audio_only()):
                raise AttributeError("No suitable audio stream found.")

            self.update_status(DownloadStatus.RUNNING)

            self.video_path = video_stream.download(output_path=str(self.base_download_path))
            self.audio_path = audio_streams.download(output_path=str(self.base_download_path))
        except (
            FileNotFoundError,
            NotImplementedError,
            ValueError,
        ) as error:
            raise DownloadError(self, error) from error
        except Exception as error:
            self._remove()
            raise DownloadError(self, error) from error

    def _multiplexage(self) -> None:
        assert self.video_path and self.audio_path
        try:
            output = ffmpeg.output(
                ffmpeg.input(filename=self.video_path),
                ffmpeg.input(filename=self.audio_path),
                filename=self.filepath,
                **app_settings.downloader.youtube.ffmpeg.model_dump(by_alias=True),
            )
            self.update_status(DownloadStatus.RUNNING, description="Multiplexage in progress...")
            output.run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as error:
            logger.error(f"stdout: {error.stdout.decode()}")
            logger.error(f"stderr: {error.stderr.decode()}")
            raise error
        finally:
            Path(self.video_path).unlink(missing_ok=True)
            Path(self.audio_path).unlink(missing_ok=True)
