from loguru import logger

from apps.celery_app import celery_app
from libs.plugins import get_downloader


@celery_app.task(bind=True)
def download_task(self, url: str, **kwargs) -> dict:
    download = get_downloader(url)(task=self, url=url, **kwargs)

    logger.info("Download started")
    download.start()
    logger.info("Download completed")

    return download.to_dict()
