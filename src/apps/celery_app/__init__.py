from celery import Celery

from config import app_settings
from services.download import plugins
from services.download.helpers.plugins import load_downloader_plugins

assert plugins

celery_app = Celery(
    "tasks",
    include=["apps.celery_app.tasks"],
    broker=app_settings.celery.broker_url,
    backend=app_settings.celery.backend_url,
    worker_concurrency=app_settings.celery.concurrency,
    broker_connection_retry_on_startup=False,
)
load_downloader_plugins()
