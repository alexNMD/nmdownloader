import importlib
from typing import Type

from nmdownloader.config import app_settings
from nmdownloader.services.download import Download
from nmdownloader.services.download_media import DownloadMedia

_PLUGIN_REGISTRY: dict[str, Type[Download | DownloadMedia]] = {}


def load_downloader_plugins():
    for path in app_settings.downloader.plugins:
        file_name, class_name = path.rsplit(".", 1)
        importlib.import_module(f"nmdownloader.plugins.{file_name}"), class_name
