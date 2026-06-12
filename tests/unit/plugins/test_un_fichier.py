"""Unit tests for plugins/un_fichier.py module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from services.download.helpers.exceptions import DownloadException
from services.download.helpers.plugins import get_downloader
from services.download.plugins.un_fichier import (
    Download1fichier,
    compute_url_from_1fichier,
)
from services.download.models.media import DownloadMedia


class TestDownload1fichier:
    """Tests for Download1fichier class."""

    def test_download_1fichier_class_exists(self):
        """Test that Download1fichier class exists."""
        assert Download1fichier is not None

    def test_download_1fichier_inheritance(self):
        """Test that Download1fichier inherits from DownloadMedia."""
        assert issubclass(Download1fichier, DownloadMedia)

    def test_download_1fichier_registration(self):
        """Test that Download1fichier is registered for 1fichier host."""
        # Import to register
        import services.download.plugins.un_fichier  # noqa: F401

        result = get_downloader("https://1fichier.com/?abc123")
        assert result == Download1fichier

    @patch("plugins.un_fichier.requests.post")
    @patch("plugins.un_fichier.requests.head")
    @patch("plugins.un_fichier.app_settings")
    def test_download_1fichier_init_with_token(
        self, mock_app_settings, mock_head, mock_post
    ):
        """Test Download1fichier initialization with API token."""
        # Setup mocks
        mock_app_settings.downloader.un_fichier.api_token = "test_token"
        mock_app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"
        mock_app_settings.media_path = Path("/tmp/media")
        mock_app_settings.downloader.plugin.registry = {}

        # Mock the token response
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {"url": "https://download.url/file"}
        mock_post_response.raise_for_status.return_value = None
        mock_post.return_value = mock_post_response

        # Mock the HEAD request for filename extraction
        mock_head_response = MagicMock()
        mock_head_response.headers = {
            "Content-Disposition": 'attachment; filename="test_file.mkv"'
        }
        mock_head.return_value = mock_head_response

        mock_task = MagicMock()

        # Create Download1fichier instance
        download = Download1fichier(url="https://1fichier.com/?abc123", task=mock_task)

        # Check that request was made to get token
        mock_post.assert_called_once()

        # Check that HEAD request was made to get filename
        mock_head.assert_called_once_with("https://download.url/file", timeout=10)

        # Check attributes - the DownloadMedia __init__ was called with the download URL
        assert download.url == "https://download.url/file"

    @patch("plugins.un_fichier.requests.post")
    @patch("plugins.un_fichier.app_settings")
    def test_download_1fichier_init_without_token(self, mock_app_settings, mock_post):
        """Test Download1fichier initialization without API token."""
        # Setup mocks - no token
        mock_app_settings.downloader.un_fichier.api_token = None
        mock_app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

        mock_task = MagicMock()

        # Should raise DownloadException
        with pytest.raises(DownloadException) as exc_info:
            Download1fichier(url="https://1fichier.com/?abc123", task=mock_task)

        assert "UNFICHIER_API_TOKEN not set" in str(exc_info.value)

    @patch("plugins.un_fichier.requests.post")
    @patch("plugins.un_fichier.requests.head")
    @patch("plugins.un_fichier.app_settings")
    def test_download_1fichier_init_with_url_splitting(
        self, mock_app_settings, mock_head, mock_post
    ):
        """Test Download1fichier initialization with URL containing ampersand."""
        mock_app_settings.downloader.un_fichier.api_token = "test_token"
        mock_app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"
        mock_app_settings.media_path = Path("/tmp/media")
        mock_app_settings.downloader.plugin.registry = {}

        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {"url": "https://download.url/file"}
        mock_post_response.raise_for_status.return_value = None
        mock_post.return_value = mock_post_response

        mock_head_response = MagicMock()
        mock_head_response.headers = {
            "Content-Disposition": 'attachment; filename="test_file.mkv"'
        }
        mock_head.return_value = mock_head_response

        mock_task = MagicMock()

        # URL with ampersand - should be split
        url = "https://1fichier.com/?abc123&param=value"

        Download1fichier(url=url, task=mock_task)

        # Check that the URL was split correctly
        # The compute_url_from_1fichier function splits on '&'
        assert mock_post.call_args[1]["json"]["url"] == "https://1fichier.com/?abc123"


class TestComputeUrlFrom1fichier:
    """Tests for compute_url_from_1fichier function."""

    @patch("plugins.un_fichier.requests.post")
    @patch("plugins.un_fichier.app_settings")
    def test_compute_url_from_1fichier_success(self, mock_app_settings, mock_post):
        """Test compute_url_from_1fichier with successful response."""
        mock_app_settings.downloader.un_fichier.api_token = "test_token"
        mock_app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

        mock_response = MagicMock()
        mock_response.json.return_value = {"url": "https://download.url/file"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = compute_url_from_1fichier(
            link="https://1fichier.com/?abc123", token="test_token"
        )

        assert result == "https://download.url/file"

    @patch("plugins.un_fichier.requests.post")
    @patch("plugins.un_fichier.app_settings")
    def test_compute_url_from_1fichier_with_error(self, mock_app_settings, mock_post):
        """Test compute_url_from_1fichier with API error."""
        mock_app_settings.downloader.un_fichier.api_token = "test_token"
        mock_app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

        # Mock to raise exception
        mock_post.side_effect = Exception("API Error")

        with pytest.raises(Exception) as exc_info:
            compute_url_from_1fichier(
                link="https://1fichier.com/?abc123", token="test_token"
            )

        assert "API Error" in str(exc_info.value)

    @patch("plugins.un_fichier.requests.post")
    @patch("plugins.un_fichier.app_settings")
    def test_compute_url_from_1fichier_http_error(self, mock_app_settings, mock_post):
        """Test compute_url_from_1fichier with HTTP error."""
        mock_app_settings.downloader.un_fichier.api_token = "test_token"
        mock_app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

        # Mock to raise HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Not Found"
        )
        mock_post.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            compute_url_from_1fichier(
                link="https://1fichier.com/?abc123", token="test_token"
            )

    @patch("plugins.un_fichier.requests.post")
    @patch("plugins.un_fichier.app_settings")
    def test_compute_url_from_1fichier_correct_request(
        self, mock_app_settings, mock_post
    ):
        """Test that compute_url_from_1fichier makes correct request."""
        mock_app_settings.downloader.un_fichier.api_token = "test_token"
        mock_app_settings.downloader.un_fichier.api_url = "https://api.1fichier.com"

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
