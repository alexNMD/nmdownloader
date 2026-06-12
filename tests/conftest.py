"""Pytest configuration and fixtures for NMDownloader tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def reset_loguru_modules():
    """Reset loguru and related modules before each test to allow patching."""
    import sys

    # Clear modules that import loguru before patching can work
    # Don't clear 'apps' as it's needed by other modules
    modules_to_clear = [
        k
        for k in list(sys.modules.keys())
        if "loguru" in k or "services.download" in k or "plugins" in k
    ]
    for mod in modules_to_clear:
        del sys.modules[mod]


@pytest.fixture
def mock_celery_task():
    """Mock Celery task for testing Download classes."""
    task = MagicMock()
    task.update_state = MagicMock()
    return task


@pytest.fixture
def mock_app_settings():
    """Mock app_settings for testing without environment variables."""
    with patch("config.base.app_settings") as mock_settings:
        # Create mock nested objects
        mock_settings.discord = MagicMock()
        mock_settings.discord.token = None
        mock_settings.discord.default_channel_id = None
        mock_settings.discord.refresh_rate = 1.0

        mock_settings.media_path = Path("/tmp/media")
        mock_settings.downloader = MagicMock()
        mock_settings.downloader.plugin = MagicMock()
        mock_settings.downloader.plugin.registry = {}
        mock_settings.downloader.youtube = MagicMock()
        mock_settings.downloader.youtube.ffmpeg = MagicMock()
        mock_settings.downloader.youtube.ffmpeg.to_dict = MagicMock(return_value={})
        mock_settings.downloader.un_fichier = MagicMock()
        mock_settings.downloader.un_fichier.api_token = None
        mock_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

        yield mock_settings


@pytest.fixture
def temp_media_path(tmp_path):
    """Create a temporary media directory for testing downloads."""
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    return media_dir


@pytest.fixture(autouse=True)
def cleanup_temp_files(tmp_path):
    """Clean up temporary files after each test."""
    yield
    # Any cleanup can be done here if needed


@pytest.fixture
def clean_registry():
    """Fixture to save and restore the plugin registry."""
    from apps.celery_app import app_settings

    original_registry = app_settings.downloader.plugin.registry.copy()
    yield
    app_settings.downloader.plugin.registry = original_registry
