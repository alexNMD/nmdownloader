"""Unit tests for plugins/un_fichier.py module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from nmdownloader.services.download.helpers.exceptions import DownloadError
from nmdownloader.services.download.helpers.plugins import get_downloader
from nmdownloader.services.download.models import DownloadMedia
from nmdownloader.services.download.plugins.un_fichier import (
    Download1fichier,
    compute_url_from_1fichier,
)


class TestDownload1fichier:
    """Tests for Download1fichier class."""

    def test_download_1fichier_class_exists(self) -> None:
        """Test that Download1fichier class exists."""
        assert Download1fichier is not None

    def test_download_1fichier_inheritance(self) -> None:
        """Test that Download1fichier inherits from DownloadMedia."""
        assert issubclass(Download1fichier, DownloadMedia)

    def test_download_1fichier_registration(self) -> None:
        """Test that Download1fichier is registered for 1fichier host."""
        # Import to register - already imported at module level
        # from services.download.plugins.un_fichier import Download1fichier

        result = get_downloader("https://1fichier.com/?abc123")
        assert result is Download1fichier

    @patch("nmdownloader.services.download.models.media.requests.head")
    @patch("nmdownloader.services.download.plugins.un_fichier.requests.post")
    def test_download_1fichier_init_with_token(self, mock_post: MagicMock, mock_head: MagicMock) -> None:
        """Test Download1fichier initialization with API token."""
        from nmdownloader.config import app_settings

        # Save original values
        original_api_token = app_settings.downloader.un_fichier.api_token
        original_api_url = app_settings.downloader.un_fichier.api_url
        original_media_path = app_settings.media_path

        try:
            # Setup mocks - set values on actual app_settings
            app_settings.downloader.un_fichier.api_token = "test_token"
            app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"
            app_settings.media_path = Path("/tmp/media")

            # Mock the token response
            mock_post_response = MagicMock()
            mock_post_response.json.return_value = {"url": "https://download.url/file"}
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            # Mock the HEAD request for filename extraction
            mock_head_response = MagicMock()
            mock_head_response.headers = {"Content-Disposition": 'attachment; filename="test_file.mkv"'}
            mock_head.return_value = mock_head_response

            mock_task = MagicMock()

            # Create Download1fichier instance
            download = Download1fichier(url="https://1fichier.com/?abc123", task=mock_task)

            # _setup() is called by start(), not in __init__, so we need to call it
            download._setup()

            # Check that request was made to get token
            mock_post.assert_called_once()

            # Check that HEAD request was made to get filename with the computed download URL
            mock_head.assert_called_once_with("https://download.url/file", timeout=10)

            # Check attributes - the URL should be the computed download URL
            assert download.url == "https://download.url/file"
        finally:
            # Restore original values
            app_settings.downloader.un_fichier.api_token = original_api_token
            app_settings.downloader.un_fichier.api_url = original_api_url
            app_settings.media_path = original_media_path

    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_1fichier_init_without_token(self, mock_head: MagicMock) -> None:
        """Test Download1fichier initialization without API token."""
        from nmdownloader.config import app_settings

        # Save original values
        original_api_token = app_settings.downloader.un_fichier.api_token
        original_api_url = app_settings.downloader.un_fichier.api_url

        try:
            # Setup mocks - no token
            app_settings.downloader.un_fichier.api_token = None
            app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

            # Mock the HEAD request for filename extraction
            mock_head_response = MagicMock()
            mock_head_response.headers = {}
            mock_head.return_value = mock_head_response

            mock_task = MagicMock()

            # Should raise DownloadError at initialization since token check is in __init__
            with pytest.raises(DownloadError) as exc_info:
                Download1fichier(url="https://1fichier.com/?abc123", task=mock_task)

            assert "UNFICHIER_API_TOKEN not set" in str(exc_info.value)
        finally:
            # Restore original values
            app_settings.downloader.un_fichier.api_token = original_api_token
            app_settings.downloader.un_fichier.api_url = original_api_url

    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_1fichier_init_without_token_with_discord_set(
        self,
        mock_head: MagicMock,
    ) -> None:
        """Test Download1fichier raises error when DISCORD_TOKEN is set."""
        from nmdownloader.config import app_settings

        # Save original values
        original_api_token = app_settings.downloader.un_fichier.api_token
        original_api_url = app_settings.downloader.un_fichier.api_url
        original_discord_token = app_settings.discord.token
        original_discord_channel = app_settings.discord.default_channel_id

        try:
            # Setup mocks - no token
            app_settings.downloader.un_fichier.api_token = None
            app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"
            # DISCORD_TOKEN is set
            app_settings.discord.token = "test_discord_token"
            app_settings.discord.default_channel_id = 123456789

            # Mock the HEAD request for filename extraction
            mock_head_response = MagicMock()
            mock_head_response.headers = {}
            mock_head.return_value = mock_head_response

            mock_task = MagicMock()

            # Should raise DownloadError at initialization since token check is in __init__
            with pytest.raises(DownloadError) as exc_info:
                Download1fichier(url="https://1fichier.com/?abc123", task=mock_task)

            assert "UNFICHIER_API_TOKEN not set" in str(exc_info.value)
        finally:
            # Restore original values
            app_settings.downloader.un_fichier.api_token = original_api_token
            app_settings.downloader.un_fichier.api_url = original_api_url
            app_settings.discord.token = original_discord_token
            app_settings.discord.default_channel_id = original_discord_channel

    @patch("nmdownloader.services.download.models.media.requests.head")
    @patch("nmdownloader.services.download.plugins.un_fichier.requests.post")
    def test_download_1fichier_init_with_url_splitting(self, mock_post: MagicMock, mock_head: MagicMock) -> None:
        """Test Download1fichier initialization with URL containing ampersand."""
        from nmdownloader.config import app_settings

        # Save original values
        original_api_token = app_settings.downloader.un_fichier.api_token
        original_api_url = app_settings.downloader.un_fichier.api_url
        original_media_path = app_settings.media_path

        try:
            app_settings.downloader.un_fichier.api_token = "test_token"
            app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"
            app_settings.media_path = Path("/tmp/media")

            mock_post_response = MagicMock()
            mock_post_response.json.return_value = {"url": "https://download.url/file"}
            mock_post_response.raise_for_status.return_value = None
            mock_post.return_value = mock_post_response

            mock_head_response = MagicMock()
            mock_head_response.headers = {"Content-Disposition": 'attachment; filename="test_file.mkv"'}
            mock_head.return_value = mock_head_response

            mock_task = MagicMock()

            # URL with ampersand - should be split
            url = "https://1fichier.com/?abc123&param=value"

            download = Download1fichier(url=url, task=mock_task)
            download._setup()

            # Check that the URL was split correctly
            # The compute_url_from_1fichier function splits on '&'
            assert mock_post.call_args[1]["json"]["url"] == "https://1fichier.com/?abc123"
        finally:
            # Restore original values
            app_settings.downloader.un_fichier.api_token = original_api_token
            app_settings.downloader.un_fichier.api_url = original_api_url
            app_settings.media_path = original_media_path


class TestComputeUrlFrom1fichier:
    """Tests for compute_url_from_1fichier function."""

    @patch("nmdownloader.services.download.plugins.un_fichier.requests.post")
    def test_compute_url_from_1fichier_success(self, mock_post: MagicMock) -> None:
        """Test compute_url_from_1fichier with successful response."""
        from nmdownloader.config import app_settings

        # Save original values
        original_api_url = app_settings.downloader.un_fichier.api_url

        try:
            app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

            mock_response = MagicMock()
            mock_response.json.return_value = {"url": "https://download.url/file"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = compute_url_from_1fichier(link="https://1fichier.com/?abc123", token="test_token")

            assert result == "https://download.url/file"
        finally:
            # Restore original values
            app_settings.downloader.un_fichier.api_url = original_api_url

    @patch("nmdownloader.services.download.plugins.un_fichier.requests.post")
    def test_compute_url_from_1fichier_with_error(self, mock_post: MagicMock) -> None:
        """Test compute_url_from_1fichier with API error."""
        from nmdownloader.config import app_settings

        # Save original values
        original_api_url = app_settings.downloader.un_fichier.api_url

        try:
            app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

            # Mock to raise exception
            mock_post.side_effect = Exception("API Error")

            with pytest.raises(Exception) as exc_info:
                compute_url_from_1fichier(link="https://1fichier.com/?abc123", token="test_token")

            assert "API Error" in str(exc_info.value)
        finally:
            # Restore original values
            app_settings.downloader.un_fichier.api_url = original_api_url

    @patch("nmdownloader.services.download.plugins.un_fichier.requests.post")
    def test_compute_url_from_1fichier_http_error(self, mock_post: MagicMock) -> None:
        """Test compute_url_from_1fichier with HTTP error."""
        from nmdownloader.config import app_settings

        # Save original values
        original_api_url = app_settings.downloader.un_fichier.api_url

        try:
            app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

            # Mock to raise HTTPError
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
            mock_post.return_value = mock_response

            with pytest.raises(requests.exceptions.HTTPError):
                compute_url_from_1fichier(link="https://1fichier.com/?abc123", token="test_token")
        finally:
            # Restore original values
            app_settings.downloader.un_fichier.api_url = original_api_url

    @patch("nmdownloader.services.download.plugins.un_fichier.requests.post")
    def test_compute_url_from_1fichier_correct_request(self, mock_post: MagicMock) -> None:
        """Test that compute_url_from_1fichier makes correct request."""
        from nmdownloader.config import app_settings

        # Save original values
        original_api_url = app_settings.downloader.un_fichier.api_url

        try:
            app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

            mock_response = MagicMock()
            mock_response.json.return_value = {"url": "https://download.url/file"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            link = "https://1fichier.com/?abc123"
            compute_url_from_1fichier(link=link, token="test_token")

            # Check request was made correctly
            mock_post.assert_called_once()

            # Check URL
            call_kwargs = mock_post.call_args
            assert "https://api.1fichier.com/download/get_token.cgi" in str(call_kwargs)

            # Check headers
            assert "Authorization" in call_kwargs[1]["headers"]
            assert call_kwargs[1]["headers"]["Authorization"] == "Bearer test_token"

            # Check JSON body
            assert call_kwargs[1]["json"]["url"] == "https://1fichier.com/?abc123"
        finally:
            # Restore original values
            app_settings.downloader.un_fichier.api_url = original_api_url
