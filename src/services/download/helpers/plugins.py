import importlib
from typing import Type
from urllib.parse import urlparse

from apps.celery_app import app_settings
from services.download.models import DownloadBase, DownloadMedia, DownloadDefault


def register_downloader(*hosts: str):
    """Decorator to register a plugin for hosts."""

    def decorator(cls: Type[DownloadBase | DownloadMedia]):
        for host in hosts:
            app_settings.downloader.plugin.registry[host] = cls
        return cls

    return decorator


def get_downloader(url: str) -> Type[DownloadBase | DownloadMedia]:
    _netloc = urlparse(url).netloc
    return app_settings.downloader.plugin.registry.get(_netloc, DownloadDefault)


def load_downloader_plugins():
    # for path in app_settings.downloader.plugin.modules:
    #     file_name, class_name = path.rsplit(".", 1)
    # try:
    importlib.import_module("services.download.plugins")
    # except ModuleNotFoundError:
    #     logger.error(f"Unable to load the plugin: {path}")
