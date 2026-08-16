from __future__ import annotations

from typing import Any

from celery import Task
from loguru import logger

from nmdownloader.apps.celery_app import celery_app
from nmdownloader.services.download.helpers.plugins import get_downloader


@celery_app.task(bind=True)
def download_task(self: Task[Any, Any], url: str, **kwargs) -> dict[str, Any]:
    download = get_downloader(url)(task=self, url=url, **kwargs)

    # TODO: do better
    download.notifier.message_id = kwargs.get("message_id")
    download.notifier.channel_id = int(kwargs.get("channel_id", 0))

    logger.info("Download started")
    download.start()
    logger.info("Download completed")

    return download.to_dict()
