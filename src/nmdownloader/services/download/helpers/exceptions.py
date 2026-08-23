from typing import TYPE_CHECKING

from celery.exceptions import Ignore
from loguru import logger

from nmdownloader.services.download.helpers.constants import DownloadStatus

if TYPE_CHECKING:
    from nmdownloader.services.download.models.base import DownloadBase


class DownloadError(Exception):
    def __init__(self, download: "DownloadBase", message: Exception | str) -> None:
        match message:
            case Exception():
                super().__init__(message)
                logger.error(message)
                download.update_status(DownloadStatus.ERROR, description=str(message))
            case str():
                super().__init__(message)
                logger.error(message)
                download.update_status(DownloadStatus.ERROR, description=message)


class DownloadRevokeException(Ignore):
    def __init__(self, download: DownloadBase, message: str = "Canceled by User") -> None:
        super().__init__(message)
        logger.info("Download Canceled")
        download.update_status(DownloadStatus.CANCELED, description=str(message))
