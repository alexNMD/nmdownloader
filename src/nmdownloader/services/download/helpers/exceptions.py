from typing import TYPE_CHECKING

from celery.exceptions import Ignore
from loguru import logger

from nmdownloader.services.download.helpers.constants import DownloadStatus

if TYPE_CHECKING:
    from nmdownloader.services.download.models.base import DownloadBase


class DownloadError(Exception):
    def __init__(self, download: "DownloadBase", message: Exception | str) -> None:
        if isinstance(message, Exception):
            super().__init__(message)
            logger.error(message)
            download.update_status(DownloadStatus.ERROR, str(message))
        else:
            super().__init__(message)
            logger.error(message)
            download.update_status(DownloadStatus.ERROR, message)


class DownloadRevokeException(Ignore):
    def __init__(self, download: DownloadBase, message: str = "Canceled by User") -> None:
        super().__init__(message)
        logger.info("Download Canceled")
        download.update_status(DownloadStatus.CANCELED, str(message))
