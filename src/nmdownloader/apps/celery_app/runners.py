from nmdownloader.apps.celery_app import celery_app
from nmdownloader.config import app_settings


def worker() -> None:
    celery_app.worker_main(
        argv=[
            "worker",
            f"--loglevel={app_settings.nmd_log_level}",
        ]
    )


def flower() -> None:
    celery_app.start(
        argv=[
            "flower",
        ]
    )
