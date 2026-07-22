from collections.abc import Callable
from typing import TypeVar
from urllib.parse import urlparse

from config import app_settings
from services.download.models import DownloadBase, DownloadDefault

T = TypeVar("T", bound=DownloadBase)


def register_downloader(*hosts: str) -> Callable[[type[T]], type[T]]:
    """Decorator to register a plugin for hosts."""

    def decorator(cls: type[T]) -> type[T]:
        for host in hosts:
            app_settings.downloader.plugin.registry[host] = cls
        return cls

    return decorator


def get_downloader(url: str) -> type[DownloadBase]:
    _netloc = urlparse(url).netloc
    return app_settings.downloader.plugin.registry.get(_netloc, DownloadDefault)
