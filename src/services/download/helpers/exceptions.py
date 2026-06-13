from celery.exceptions import Ignore
from loguru import logger

from services.download.helpers.constants import DownloadStatus


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
