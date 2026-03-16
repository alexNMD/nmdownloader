import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.libs.download import (
    compute_url_from_1fichier,
    DownloadException,
    DownloadRevokeException,
    DownloadStatus,
)
from nmdownloader.services.discord_api import DiscordAPI

discord_api = DiscordAPI()


class Download(ABC):
    def __init__(
        self,
        task: Any,  # Celery Task
        type_dl: str,
        filepath: Path,
        message_id=None,
        channel_id=None,
    ):
        self.task = task
        self.filepath = filepath
        self.filename = self.filepath.name
        self.status_message_id = None
        self.message_id = message_id
        self.channel_id = channel_id or app_settings.discord.default_channel_id
        self.type_dl = type_dl

    @abstractmethod
    def start(self):
        pass

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

    def _compute_url(self, url) -> str:
        download_providers = {"1fichier.com": compute_url_from_1fichier}
        _netloc = urlparse(url).netloc

        try:
            return download_providers.get(_netloc, lambda _url: url)(url)
        except Exception as error:
            raise DownloadException(self, str(error))

    def _remove(self) -> None:
        if self.filepath.exists():
            self.filepath.unlink(missing_ok=True)
            logger.info(f"file removed: {self.filepath}")
