from nmdownloader.apps.celery_app import celery_app
from nmdownloader.services.download import Download


@celery_app.task(bind=True)
def download_task(self, **kwargs) -> dict:
    download = Download(task=self, **kwargs)

    download.check()

    download.start()

    return download.to_dict()
