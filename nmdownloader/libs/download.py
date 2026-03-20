from enum import Enum

from celery.exceptions import Ignore
from loguru import logger


class DownloadStatus(Enum):
    STARTED = int("e8f30b", 16)
    RUNNING = int("f3ad0b", 16)
    DONE = int("0dba2f", 16)
    ERROR = int("f63106", 16)
    CANCELED = int("510666", 16)


class DownloadException(Exception):
    def __init__(self, download, message):
        super().__init__(message)
        logger.error(message)
        download.update_status(DownloadStatus.ERROR, str(message))


class DownloadRevokeException(Ignore):
    def __init__(self, download, message="Canceled by User"):
        super().__init__(message)
        logger.info("Download Canceled")
        download.update_status(DownloadStatus.CANCELED, str(message))
