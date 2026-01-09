from loguru import logger

from nmdownloader.apps.celery_app import celery_app
from nmdownloader.services.download import Download


@celery_app.task(bind=True)
def download_task(self, **kwargs) -> dict:
    download = Download(task=self, **kwargs)
    logger.info(f"Downloading {download.filename}")

    download.check()
    logger.info(f"Check passed for {download.filename}")

    download.start()
    logger.info(f"Download completed for {download.filename}")

    return download.to_dict()
