from __future__ import annotations

from typing import Any

from celery import Task
from loguru import logger

from nmdownloader.apps.celery_app import celery_app
from nmdownloader.services.download.helpers.plugins import get_downloader


@celery_app.task(bind=True)
def download_task(self: Task[Any, Any], url: str, **kwargs) -> dict[str, Any]:
    download = get_downloader(url)(task=self, url=url, **kwargs)

    if kwargs.get("message_id") is not None:
        download.notifier.message_id = kwargs["message_id"]
    if kwargs.get("channel_id") is not None:
        download.notifier.message_id = kwargs["channel_id"]

    logger.info("Download started")
    download.start()
    logger.info("Download completed")

    return download.to_dict()
