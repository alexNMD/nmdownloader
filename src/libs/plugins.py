from typing import Type
from urllib.parse import urlparse

from src.config.base import app_settings
from src.services.download import Download
from src.services.download_default import DownloadDefault
from src.services.download_media import DownloadMedia


def register_downloader(*hosts: str):
    """Decorator to register a plugin for hosts."""

    def decorator(cls: Type[Download | DownloadMedia]):
        for host in hosts:
            app_settings.downloader.plugin.registry[host] = cls
        return cls

    return decorator


def get_downloader(url: str) -> Type[Download | DownloadMedia]:
    _netloc = urlparse(url).netloc
    return app_settings.downloader.plugin.registry.get(_netloc, DownloadDefault)
