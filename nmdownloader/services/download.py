import io
import json
import re
import time
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

import requests

import unzipall  # type: ignore
from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.libs.download import (
    compute_url_from_1fichier,
    extract_filename,
    DownloadException,
    DownloadRevokeException,
    DownloadStatus,
)
from nmdownloader.libs.files import get_relative_directory
from nmdownloader.libs.progressbar import get_progress_bar
from nmdownloader.services.discord_api import DiscordAPI

discord_api = DiscordAPI()


class ShowType(Enum):
    SERIES = "series"
    FILMS = "films"
    ANIMES = "animes"


class Download:
    def __init__(self, url, task, message_id=None, channel_id=None, type_dl=None):
        self.task = task
        self.status_message_id = None
        self.message_id = message_id
        self.channel_id = channel_id or app_settings.discord.default_channel_id
        self.url = self._compute_url(url)
        try:
            self.filename = extract_filename(self.url)
        except ValueError:
            *_, self.filename = self.url.split("/")
        except Exception as error:
            raise DownloadException(self, "Unable to retrieve filename") from error
        self.filename_path = Path(self.filename)
        self.type_dl = (
            (
                ShowType.SERIES.value
                if re.search(r"[Ss]\d{1,2}([Ee]\d{1,2})?", self.filename)
                else ShowType.FILMS.value
            )
            if not type_dl
            else type_dl
        )
        self.is_compressed = (
            True
            if self.filename_path.suffix in unzipall.list_supported_formats()
            else False
        )
        self.base_download_path: Path = app_settings.media_path / self.type_dl
        self.destination_directory: Path = (
            self.base_download_path / get_relative_directory(self.filename_path)
            if self.type_dl in [ShowType.SERIES.value, ShowType.ANIMES.value]
            else self.base_download_path
        )
        self.filepath = self.destination_directory / self.filename_path
        self.downloaded_size = 0
        self.download_start_time = None
        self.download_speed = None
        self.total_size = None
        self.finished = False

    def check(self):
        if not self.base_download_path.exists():
            raise DownloadException(self, f"{self.base_download_path} doesn't exist")

        # TODO: refacto. find a better way
        # if dest_file_exists(self.file_path):
        #     raise DownloadException(self, "Already exist")

        return True

    def start(self):
        try:
            self.destination_directory.mkdir(parents=True, exist_ok=True)
            with requests.get(self.url, stream=True, timeout=3600) as response:
                if response.ok:
                    self.update_status(DownloadStatus.STARTED)
                    self.total_size = int(response.headers.get("Content-Length", 0))
                    self.download_start_time = time.time()

                    ### Start reading file
                    with open(self.filepath, "wb") as file:
                        with io.BufferedWriter(
                            file,
                            buffer_size=(1024 * 64),  # 64 KB
                        ) as file_buffer:
                            self._handle_chunks(file_buffer, response)
                    ### Close file

                    if self.is_compressed:
                        self._decompress()

                    ### Finish
                    self.finished = True
                    self.update_status(DownloadStatus.DONE)
        except (
            FileNotFoundError,
            NotImplementedError,
            ValueError,
            unzipall.ArchiveExtractionError,
        ) as error:
            raise DownloadException(self, error) from error
        except Exception as error:
            self._remove()
            raise DownloadException(self, error) from error

    def cancel(self):
        self._remove()
        raise DownloadRevokeException(self)

    def to_dict(self) -> dict:
        download_dict = {}
        for key, value in self.__dict__.items():
            match value:
                case Path():
                    download_dict[key] = str(value)
                case _:
                    try:
                        json.dumps(value)
                        download_dict[key] = value
                    except (TypeError, OverflowError):
                        pass
        return download_dict

    def update_status(
        self, status: DownloadStatus, additional: str = str(), meta_data=None
    ) -> None:
        title = f"Download {status.name}"
        _base_content = (
            ""
            if not (hasattr(self, "type_dl") and hasattr(self, "filename"))
            else f"[{self.type_dl}] {self.filename}\n"
        )
        content = f"{_base_content}{additional}" if additional else _base_content

        self.task.update_state(meta=self.to_dict())
        self._do_notification(status, title, content)

    def _do_notification(self, status: DownloadStatus, title, content) -> None:
        logger.info(f"{title} => {content}")

        if self.status_message_id:
            discord_api.edit_embed(
                self.channel_id, self.status_message_id, title, content, status.value
            )
            return

        self.status_message_id = (
            discord_api.reply_with_embed(
                self.channel_id, self.message_id, title, content, status.value
            )
            if self.message_id
            else discord_api.send_embed(self.channel_id, title, content, status.value)
        )

    def _decompress(self) -> None:
        self.update_status(
            DownloadStatus.RUNNING, additional="Extraction in progress..."
        )

        logger.info(f"{self.filename} extraction in progress...")
        unzipall.extract(
            archive_path=self.filepath, extract_to=self.destination_directory
        )
        self._remove()
        logger.info(f"{self.filename} extraction done")

    def _compute_url(self, url) -> str:
        download_providers = {"1fichier.com": compute_url_from_1fichier}
        _netloc = urlparse(url).netloc

        try:
            return download_providers.get(_netloc, lambda _url: url)(url)
        except Exception as error:
            raise DownloadException(self, str(error))

    def _handle_chunks(self, file_buffer, response) -> None:
        _count_refresh = 0

        for chunk in response.iter_content(chunk_size=1024 * 64):
            if not chunk:
                break

            file_buffer.write(chunk)

            self.downloaded_size += len(chunk)
            _elapsed_time = time.time() - self.download_start_time
            _refresh_interval_count = int(
                _elapsed_time / app_settings.discord.refresh_rate
            )

            if _refresh_interval_count > _count_refresh:
                _count_refresh += 1
                self.download_speed = self.downloaded_size / _elapsed_time
                self.update_status(
                    DownloadStatus.RUNNING, additional=self._compute_progress()
                )

    def _remove(self) -> None:
        if self.filepath.exists():
            self.filepath.unlink(missing_ok=True)
            logger.info(f"file removed: {self.filepath}")

    def _compute_progress(self) -> str:
        _remaining_time_seconds = (
            self.total_size - self.downloaded_size
        ) / self.download_speed
        _less_than_one_minute = _remaining_time_seconds < 60

        progress_bar = get_progress_bar(self.downloaded_size, self.total_size)
        remaining_time = (
            _remaining_time_seconds
            if _less_than_one_minute
            else _remaining_time_seconds / 60
        )
        time_unit = "sec" if _less_than_one_minute else "min"
        speed_in_mb = self.download_speed / (1024 * 1024)

        return f"{progress_bar} [ETA {remaining_time:.0f} {time_unit} @ {speed_in_mb:.2f} MB/s]"
