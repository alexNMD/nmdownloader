import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

import requests
from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.services.discord import DiscordAPI
from nmdownloader.services.download.helpers import DownloadRevokeException, DownloadStatus

if TYPE_CHECKING:
    from celery import Task


class DownloadBase(ABC):
    def __init__(
        self,
        task: Task | None,
        filepath: Path,
        message_id: int | None = None,
        channel_id: int | None = None,
        **kwargs,
    ) -> None:
        self.task = task
        self.filepath = filepath
        self.message_id = message_id
        self.channel_id = channel_id or app_settings.discord.default_channel_id
        self.options = kwargs
        self.status_message_id = None

    @abstractmethod
    def start(self) -> None:
        pass

    def _remove(self) -> None:
        self.filepath.unlink(missing_ok=True)
        logger.info(f"file removed: {self.filepath}")

    def cancel(self) -> None:
        self._remove()
        raise DownloadRevokeException(self)

    def to_dict(self) -> dict[str, Any]:
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

    def update_status(self, status: DownloadStatus, additional: str = "") -> None:
        _base_content = f"[{self.__class__.__name__}]"
        if hasattr(self, "filepath"):
            _base_content += f" {self.filepath.name}"

        title = f"Download {status.name}"
        content = f"{_base_content} {additional}" if additional else _base_content

        if hasattr(self, "task") and self.task is not None:
            self.task.update_state(meta=self.to_dict())
        self._do_notification(status, title, content)

    def _do_notification(self, status: DownloadStatus, title: str, content: str) -> None:
        logger.info(f"{title} => {content}")

        status_message_id = getattr(self, "status_message_id", None)
        channel_id = getattr(self, "channel_id", app_settings.discord.default_channel_id)
        message_id = getattr(self, "message_id", None)

        if not app_settings.discord.token:
            logger.debug("DISCORD_TOKEN not set. Unable to send notification")
            return
        if not channel_id:
            logger.error("DISCORD_DEFAULT_CHANNEL_ID not set. Unable to send notification")
            return

        try:
            if status_message_id:
                DiscordAPI.edit_embed(channel_id, status_message_id, title, content, status.value)
                return

            self.status_message_id = (
                DiscordAPI.reply_with_embed(channel_id, message_id, title, content, status.value)
                if message_id
                else DiscordAPI.send_embed(channel_id, title, content, status.value)
            )
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code == 401:
                logger.error("DISCORD_TOKEN invalid. Unable to send notification")
                return
            logger.error(f"Unable to use discord api, got: {http_error.response.status_code}")
        except requests.exceptions.RequestException as error:
            logger.error(f"Unable to reach Discord API: {error}")
