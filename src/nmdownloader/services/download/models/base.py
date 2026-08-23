from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger

from nmdownloader.services.download.helpers import DownloadRevokeException, DownloadStatus
from nmdownloader.services.notification import Notifier

if TYPE_CHECKING:
    from celery import Task


class DownloadBase(ABC):
    def __init__(self, task: Task[Any, Any]) -> None:
        self.task = task
        self.notifier = Notifier()

    @property
    @abstractmethod
    def filepath(self) -> Path: ...

    @abstractmethod
    def _setup(self) -> None: ...

    @abstractmethod
    def _download(self) -> None: ...

    @abstractmethod
    def _terminate(self) -> None: ...

    def start(self) -> None:
        self._setup()
        self._download()
        self._terminate()

    def _remove(self) -> None:
        self.filepath.unlink(missing_ok=True)
        logger.info(f"file removed: {self.filepath}")

    def cancel(self) -> None:
        self._remove()
        raise DownloadRevokeException(self)

    def to_dict(self) -> dict[str, Any]:
        download_dict = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
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
        self.task.update_state(meta=self.to_dict())
        self.notifier.throw(status=status, download=self, **kwargs)
