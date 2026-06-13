"""Pytest configuration and fixtures for NMDownloader tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


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
def clean_registry():
    """Fixture to save and restore the plugin registry."""
    from config import app_settings

    original_registry = app_settings.downloader.plugin.registry.copy()
    yield
    app_settings.downloader.plugin.registry = original_registry
