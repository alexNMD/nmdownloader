"""Pytest configuration and fixtures for NMDownloader tests."""

from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    pass


# Global mock for requests module to prevent any real HTTP calls during testing
@pytest.fixture(autouse=True)
def mock_requests_module() -> Generator[None, None, None]:
    """
    Global fixture that mocks the requests module to prevent real HTTP requests.
    This ensures that no real API calls are made during testing, even if API tokens are configured.
    """
    # Create a safe mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_response.headers = {}

    # Mock all the main request methods
    with (
        patch("requests.get") as mock_get,
        patch("requests.post") as mock_post,
        patch("requests.put") as mock_put,
        patch("requests.delete") as mock_delete,
        patch("requests.patch") as mock_patch,
        patch("requests.request") as mock_request,
        patch("requests.head") as mock_head,
    ):
        # Set return values for all mocked methods
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_put.return_value = mock_response
        mock_delete.return_value = mock_response
        mock_patch.return_value = mock_response
        mock_request.return_value = mock_response
        mock_head.return_value = mock_response

        yield


@pytest.fixture(autouse=True)
def mock_pytubefix() -> Generator[MagicMock, None, None]:
    """
    Global fixture that mocks pytubefix.YouTube to prevent real YouTube API calls.
    """
    with patch("pytubefix.YouTube") as mock_youtube_class:
        # Create a mock YouTube instance with safe defaults
        mock_youtube_instance = MagicMock()
        mock_youtube_instance.title = "Test Video"
        mock_youtube_instance.thumbnail_url = "https://example.com/thumbnail.jpg"
        mock_youtube_instance.streams = MagicMock()
        mock_youtube_instance.streams.get_highest_resolution.return_value = MagicMock()
        mock_youtube_instance.streams.get_audio_only.return_value = [MagicMock()]

        mock_youtube_class.return_value = mock_youtube_instance
        yield mock_youtube_class


@pytest.fixture(autouse=True)
def mock_api_tokens() -> Generator[None, None, None]:
    """
    Global fixture that patches only the API tokens in app_settings to None
    to prevent real API calls, even if environment variables are configured.
    This preserves the structure of app_settings to avoid breaking plugin registration.
    """
    # Import the real app_settings first to preserve structure
    from nmdownloader.config import app_settings

    # Save original values
    original_discord_token = app_settings.discord.token
    original_discord_channel: int = app_settings.discord.default_channel_id
    original_tmdb_key = app_settings.tmdb.api_key
    original_unfichier_token = app_settings.downloader.un_fichier.api_token

    # Set tokens to None/0 to prevent real API calls
    app_settings.discord.token = None
    app_settings.discord.default_channel_id = 0
    app_settings.tmdb.api_key = None
    app_settings.downloader.un_fichier.api_token = None

    try:
        yield
    finally:
        # Restore original values
        app_settings.discord.token = original_discord_token
        app_settings.discord.default_channel_id = original_discord_channel
        app_settings.tmdb.api_key = original_tmdb_key
        app_settings.downloader.un_fichier.api_token = original_unfichier_token


@pytest.fixture
def mock_app_settings() -> Generator[MagicMock, None, None]:
    """Mock app_settings for testing without environment variables."""
    with patch("nmdownloader.config.app_settings") as mock_settings:
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
def clean_registry() -> Generator[None, None, None]:
    """Fixture to save and restore the plugin registry."""
    from nmdownloader.config import app_settings

    original_registry = app_settings.downloader.plugin.registry.copy()
    yield
    app_settings.downloader.plugin.registry = original_registry
