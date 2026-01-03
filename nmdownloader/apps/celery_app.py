from celery import Celery

from nmdownloader.config import app_settings

celery_app = Celery(
    "tasks",
    include=["nmdownloader.tasks"],
    broker=app_settings.celery.broker_url,
    backend=app_settings.celery.backend_url,
    worker_concurrency=app_settings.celery.concurrency,
    broker_connection_retry_on_startup=False,
    task_serializer="pickle",
    accept_content=["pickle", "json"],
    worker_send_task_events=True,
)
