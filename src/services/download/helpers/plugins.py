from typing import Type
from urllib.parse import urlparse

from config import app_settings
from services.download.models import DownloadBase, DownloadMedia, DownloadDefault


def register_downloader(*hosts: str):
    """Decorator to register a plugin for hosts."""

    def decorator(cls: Type[DownloadBase | DownloadMedia]):
        for host in hosts:
            app_settings.downloader.plugin.registry[host] = cls
        return cls

    return decorator


def get_downloader(url: str) -> type[DownloadBase]:
    _netloc = urlparse(url).netloc
    return app_settings.downloader.plugin.registry.get(_netloc, DownloadDefault)
