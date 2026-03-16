from loguru import logger

from nmdownloader.apps.celery_app import celery_app
from nmdownloader.services.download_media import DownloadMedia


@celery_app.task(bind=True)
def download_media_task(self, **kwargs) -> dict:
    download = DownloadMedia(task=self, **kwargs)
    logger.info(f"Downloading {download.filename}")

    download.start()
    logger.info(f"Download completed for {download.filename}")

    return download.to_dict()
