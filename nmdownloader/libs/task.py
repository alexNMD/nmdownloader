from typing import Type
from urllib.parse import urlparse

from celery.result import AsyncResult

from nmdownloader.apps.celery_app import celery_app
from nmdownloader.plugins.download_1fichier import Download1fichier
from nmdownloader.plugins.download_default import DownloadDefault
from nmdownloader.plugins.download_youtube import DownloadYoutube
from nmdownloader.services.download import Download
from nmdownloader.services.download_media import DownloadMedia


def get_task_result(task_id: str) -> dict:
    result: AsyncResult = AsyncResult(task_id, app=celery_app)
    info = str(result.info) if isinstance(result.info, Exception) else result.info
    return dict(successful=result.successful(), status=result.status, info=info)


def get_downloader(url: str) -> Type[Download | DownloadMedia]:
    plugins = {
        "1fichier.com": Download1fichier,
        "www.youtube.com": DownloadYoutube,
    }
    _netloc = urlparse(url).netloc

    return plugins.get(_netloc, DownloadDefault)
