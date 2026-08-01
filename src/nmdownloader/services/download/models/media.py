import io
import re
import time
from enum import Enum
from pathlib import Path
from typing import cast

import requests
import unzipall
from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.services.download.helpers import DownloadStatus
from nmdownloader.services.download.helpers.exceptions import DownloadError
from nmdownloader.services.download.helpers.files import get_relative_directory
from nmdownloader.services.download.helpers.progressbar import get_progress_bar
from nmdownloader.services.download.models import DownloadBase


class ShowType(Enum):
    SERIES = "series"
    FILMS = "films"
    ANIMES = "animes"


class DownloadMedia(DownloadBase):
    REGEX_SEARCH_TYPE = r"[Ss]\d{1,2}([Ee]\d{1,2})?"

    def __init__(self, url: str, **kwargs) -> None:
        self.url: str = url
        try:
            self.filename: str = self._extract_filename(url=self.url)
        except ValueError as error:
            raise DownloadError(self, "Unable to retrieve filename") from error
        except Exception as error:
            raise DownloadError(self, f"Unable to retrieve filename. Reason: {error}") from error
        self.type_dl: str = kwargs.get("type_dl") or (
            ShowType.SERIES.value if re.search(self.REGEX_SEARCH_TYPE, self.filename) else ShowType.FILMS.value
        )
        self.base_download_path: Path = app_settings.media_path / self.type_dl
        self.destination_directory: Path = (
            self.base_download_path / get_relative_directory(self.filename)
            if self.type_dl in [ShowType.SERIES.value, ShowType.ANIMES.value]
            else self.base_download_path
        )
        self.downloaded_size: int = 0
        self.download_start_time: float = 0.0
        self.download_speed: float
        self.total_size: int = 0

        super().__init__(filepath=self.destination_directory / self.filename, **kwargs)

    @property
    def is_compressed(self) -> bool:
        return Path(self.filepath).suffix in unzipall.list_supported_formats()

    @classmethod
    def _extract_filename(cls, url: str) -> str:
        _content_disposition = requests.head(url, timeout=10).headers.get("Content-Disposition", "")
        _filename_regex = r'filename\*?=(?:UTF-8\'\')?"?([^;\n"]+)"?'

        if _match := re.search(_filename_regex, _content_disposition):
            return _match.group(1).replace(" ", ".")

        *_, filename = url.split("/")
        if not filename:
            raise ValueError

        return filename.replace(" ", ".")

    def start(self) -> None:
        try:
            self.destination_directory.mkdir(parents=True, exist_ok=True)
            with requests.get(self.url, stream=True, timeout=3600) as response:
                if response.ok:
                    self.update_status(DownloadStatus.STARTED)
                    self.total_size = int(response.headers.get("Content-Length", 0))
                    self.download_start_time = time.time()

                    # Start reading file
                    with (
                        open(self.filepath, "wb") as file,
                        io.BufferedWriter(
                            file,
                            buffer_size=(1024 * 64),  # 64 KB
                        ) as file_buffer,
                    ):
                        self._handle_chunks(cast(io.BufferedWriter, file_buffer), response)
                    # Close file

                    if self.is_compressed:
                        self._decompress()

                    # Finish
                    self.update_status(DownloadStatus.DONE)
        except (
            FileNotFoundError,
            NotImplementedError,
            ValueError,
            unzipall.ArchiveExtractionError,
        ) as error:
            raise DownloadError(self, error) from error
        except Exception as error:
            self._remove()
            raise DownloadError(self, error) from error

    def _handle_chunks(self, file_buffer: io.BufferedWriter, response: requests.Response) -> None:
        _count_refresh = 0

        for chunk in response.iter_content(chunk_size=1024 * 64):
            if not chunk:
                break

            file_buffer.write(chunk)

            self.downloaded_size += len(chunk)
            _elapsed_time = time.time() - self.download_start_time
            _refresh_interval_count = int(_elapsed_time / app_settings.discord.refresh_rate)

            if _refresh_interval_count > _count_refresh:
                _count_refresh += 1
                self.download_speed = self.downloaded_size / _elapsed_time
                self.update_status(DownloadStatus.RUNNING, additional=self._compute_progress())

    def _compute_progress(self) -> str:
        _remaining_time_seconds = (self.total_size - self.downloaded_size) / self.download_speed
        _less_than_one_minute = _remaining_time_seconds < 60

        progress_bar = get_progress_bar(self.downloaded_size, self.total_size)
        remaining_time = _remaining_time_seconds if _less_than_one_minute else _remaining_time_seconds / 60
        time_unit = "sec" if _less_than_one_minute else "min"
        speed_in_mb = self.download_speed / (1024 * 1024)

        return f"{progress_bar} [ETA {remaining_time:.0f} {time_unit} @ {speed_in_mb:.2f} MB/s]"

    def _decompress(self) -> None:
        self.update_status(DownloadStatus.RUNNING, additional="Extraction in progress...")

        logger.info(f"{self.filename} extraction in progress...")
        unzipall.extract(archive_path=self.filepath, extract_to=self.destination_directory)
        self._remove()
        logger.info(f"{self.filename} extraction done")
