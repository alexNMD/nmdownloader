import pickle

from nmdownloader.apps.celery_app import celery_app
from nmdownloader.services.download_handler import DownloadHandler


@celery_app.task(bind=True)
def download_task(self, **kwargs) -> dict:
    download = DownloadHandler(task=self, **kwargs)

    download.check()

    download.start()

    return dict(download=pickle.dumps(download))
