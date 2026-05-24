from celery import Celery

from src.config.base import app_settings
from src.plugins import load_downloader_plugins

celery_app = Celery(
    "tasks",
    include=["src.tasks"],
    broker=app_settings.celery.broker_url,
    backend=app_settings.celery.backend_url,
    worker_concurrency=app_settings.celery.concurrency,
    broker_connection_retry_on_startup=False,
)
load_downloader_plugins()
