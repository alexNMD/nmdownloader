from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

from nmdownloader.services.download.helpers import DownloadRevokeException, DownloadStatus
from nmdownloader.services.notification import DiscordAPI, NotificationError

if TYPE_CHECKING:
    from celery import Task


class DownloadBase(ABC):
    channel_id: int | None = None
    message_id: int | None = None
    status_message_id: int | None = None
    thumbnail: str | None = None

    def __init__(
        self,
        task: Task[Any, Any] | None,
        filepath: Path,
        message_id: int | None = None,
        channel_id: int | None = None,
        **kwargs,
    ) -> None:
        self.task = task
        self.filepath = filepath
        self.message_id = message_id
        self.channel_id = channel_id
        self.options: dict[str, Any] = kwargs
        self.status_message_id: int | None = None

    def start(self) -> None:
        self._setup()
        self._download()
        self._terminate()

    @abstractmethod
    def _setup(self) -> None: ...

    @abstractmethod
    def _download(self) -> None: ...

    @abstractmethod
    def _terminate(self) -> None: ...

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

    def update_status(self, status: DownloadStatus, **kwargs) -> None:
        if hasattr(self, "task") and self.task is not None:
            self.task.update_state(meta=self.to_dict())
        self._do_notification(status=status, **kwargs)

    def _do_notification(self, status: DownloadStatus, **kwargs) -> None:
        title = self.filepath.name if hasattr(self, "filepath") else self.__class__.__name__
        fields = [{"name": "Status", "value": status.name}]

        logger.info(f"{title} => {status.name}")

        embed_payload = {
            "title": title,
            "color": status.value,
            "fields": fields,
            "thumbnail": self.thumbnail,
            **kwargs,
        }

        try:
            if self.status_message_id:
                DiscordAPI.edit_embed(message_id=self.status_message_id, channel_id=self.channel_id, **embed_payload)
                return

            self.status_message_id = (
                DiscordAPI.reply_with_embed(message_id=self.message_id, channel_id=self.channel_id, **embed_payload)
                if self.message_id
                else DiscordAPI.send_embed(channel_id=self.channel_id, **embed_payload)
            )
        except NotificationError:
            logger.error("Notification Failed")
            return
