from typing import Type
from urllib.parse import urlparse

from nmdownloader.services.download import Download
from nmdownloader.services.download_default import DownloadDefault
from nmdownloader.services.download_media import DownloadMedia

_DOWNLOADER_PLUGIN_REGISTRY: dict[str, Type[Download | DownloadMedia]] = {}


def register_downloader(*hosts: str):
    """Decorator to register a plugin for hosts."""

    def decorator(cls: Type[Download | DownloadMedia]):
        for host in hosts:
            _DOWNLOADER_PLUGIN_REGISTRY[host] = cls
        return cls

    return decorator


def get_downloader(url: str) -> Type[Download | DownloadMedia]:
    _netloc = urlparse(url).netloc
    return _DOWNLOADER_PLUGIN_REGISTRY.get(_netloc, DownloadDefault)
