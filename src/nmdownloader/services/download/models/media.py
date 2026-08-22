import io
import re
import time
from functools import cached_property
from pathlib import Path
from typing import cast

import requests
import unzipall
from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.services.notification import TMDBApi

from ..helpers import DownloadError, DownloadStatus, get_media_name, get_progress_bar, get_relative_directory
from ..helpers.constants import ShowType
from ..models import DownloadBase


class DownloadMedia(DownloadBase):
    REGEX_SEARCH_TYPE = r"[Ss]\d{1,2}([Ee]\d{1,2})?"

    def __init__(self, url: str, **kwargs) -> None:
        self.url: str = url
        self.type_dl: str = kwargs.get("type_dl") or (
            ShowType.SERIES.value if re.search(self.REGEX_SEARCH_TYPE, self.filename) else ShowType.FILMS.value
        )
        self.thumbnail = TMDBApi.get_thumbnail(query=get_media_name(filename=self.filename, type_dl=self.type_dl))
        self.base_download_path: Path = app_settings.media_path / self.type_dl
        self.destination_directory: Path = (
            self.base_download_path / get_relative_directory(self.filename)
            if self.type_dl in [ShowType.SERIES.value, ShowType.ANIMES.value]
            else self.base_download_path
        )
        self.downloaded_size: int = 0
        self.download_start_time: float = 0.0
        self.download_speed: float

        super().__init__(filepath=self.destination_directory / self.filename, **kwargs)

    @property
    def is_compressed(self) -> bool:
        return Path(self.filepath).suffix in unzipall.list_supported_formats()

    @cached_property
    def _get_headers(self) -> dict[str, str | int]:
        try:
            with requests.head(url=self.url, timeout=10) as response:
                return dict(**response.headers)
        except Exception as error:
            raise DownloadError(self, f"Unable to fetch headers. Reason: {error}") from error

    @cached_property
    def filename(self) -> str:
        try:
            return self._extract_filename()
        except ValueError as error:
            raise DownloadError(self, "Unable to retrieve filename") from error
        except Exception as error:
            raise DownloadError(self, f"Unable to retrieve filename. Reason: {error}") from error

    @cached_property
    def total_size(self) -> int:
        return int(self._get_headers.get("Content-Length", 0))

    def _setup(self) -> None:
        self.update_status(DownloadStatus.STARTED)
        self.destination_directory.mkdir(parents=True, exist_ok=True)

    def _terminate(self) -> None:
        if self.is_compressed:
            self._decompress()
        self.update_status(DownloadStatus.DONE)

    def _extract_filename(self) -> str:
        _content_disposition = self._get_headers.get("Content-Disposition", "")
        _filename_regex = r'filename\*?=(?:UTF-8\'\')?"?([^;\n"]+)"?'

        if _match := re.search(_filename_regex, str(_content_disposition)):
            return _match.group(1).replace(" ", ".")

        *_, filename = self.url.split("/")
        if not filename:
            raise ValueError

        return filename.replace(" ", ".")

    def _download(self) -> None:
        try:
            with requests.get(self.url, stream=True, timeout=3600) as response:
                if response.ok:
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
                self.update_status(DownloadStatus.RUNNING, description=self._compute_progress())

    def _compute_progress(self) -> str:
        _remaining_time_seconds = (self.total_size - self.downloaded_size) / self.download_speed
        _less_than_one_minute = _remaining_time_seconds < 60

        progress_bar = get_progress_bar(self.downloaded_size, self.total_size)
        remaining_time = _remaining_time_seconds if _less_than_one_minute else _remaining_time_seconds / 60
        time_unit = "sec" if _less_than_one_minute else "min"
        speed_in_mb = self.download_speed / (1024 * 1024)

        return f"{progress_bar} [ETA {remaining_time:.0f} {time_unit} @ {speed_in_mb:.2f} MB/s]"

    def _decompress(self) -> None:
        self.update_status(DownloadStatus.RUNNING, description="Extraction in progress...")

        logger.info(f"{self.filename} extraction in progress...")
        unzipall.extract(archive_path=self.filepath, extract_to=self.destination_directory)
        self._remove()
        logger.info(f"{self.filename} extraction done")
