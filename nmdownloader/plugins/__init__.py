import importlib

from loguru import logger

from nmdownloader.config.base import app_settings


def load_downloader_plugins():
    for path in app_settings.downloader.plugin.modules:
        file_name, class_name = path.rsplit(".", 1)
        try:
            importlib.import_module(f"nmdownloader.plugins.{file_name}"), class_name
        except ModuleNotFoundError:
            logger.error(f"Unable to load the plugin: {path}")
            continue
