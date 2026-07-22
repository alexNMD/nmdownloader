import importlib

from celery import Celery

from nmdownloader.config import app_settings
from nmdownloader.services.download import plugins

assert plugins

celery_app = Celery(
    "tasks",
    include=["nmdownloader.apps.celery_app.tasks"],
    broker=app_settings.celery.broker_url,
    backend=app_settings.celery.backend_url,
    worker_concurrency=app_settings.celery.concurrency,
    broker_connection_retry_on_startup=False,
    worker_send_task_events=True,
)
importlib.import_module("nmdownloader.services.download.plugins")
