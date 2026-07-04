"""Unit tests for plugins/youtube.py module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.download.helpers.exceptions import DownloadException
from services.download.helpers.plugins import get_downloader
from services.download.models import DownloadBase
from services.download.plugins.youtube import DownloadYoutube


class TestDownloadYoutube:
    """Tests for DownloadYoutube class."""

    def test_download_youtube_class_exists(self):
        """Test that DownloadYoutube class exists."""
        assert DownloadYoutube is not None

    def test_download_youtube_inheritance(self):
        """Test that DownloadYoutube inherits from Download."""
        assert issubclass(DownloadYoutube, DownloadBase)

    def test_download_youtube_registration(self):
        """Test that DownloadYoutube is registered for YouTube hosts."""
        # Import to register

        youtube_hosts = ["www.youtube.com", "youtube.com", "youtu.be"]

        for host in youtube_hosts:
            result = get_downloader(f"https://{host}/watch?v=test")
            assert result is DownloadYoutube

    @patch("services.download.plugins.youtube.YouTube")
    @patch("services.download.plugins.youtube.secure_filename")
    def test_download_youtube_init(self, mock_secure_filename, mock_youtube):
        """Test DownloadYoutube initialization."""
        # Setup mocks
        mock_youtube_instance = MagicMock()
        mock_youtube_instance.title = "Test Video Title"
        mock_youtube.return_value = mock_youtube_instance

        mock_secure_filename.return_value = "Test_Video_Title.mp4"

        mock_task = MagicMock()

        # Create DownloadYoutube instance
        download = DownloadYoutube(
            url="https://www.youtube.com/watch?v=test", task=mock_task
        )

        # Check attributes
        assert download.youtube_obj == mock_youtube_instance
        assert download.filename == "Test_Video_Title.mp4"
        # The base_download_path uses app_settings.media_path (default is /media)
        assert download.base_download_path == Path("/media") / "youtube"
        assert "youtube" in str(download.filepath)

        # Verify YouTube was called with correct URL
        mock_youtube.assert_called_once_with(url="https://www.youtube.com/watch?v=test")

    @patch("services.download.plugins.youtube.YouTube")
    @patch("services.download.plugins.youtube.secure_filename")
    def test_download_youtube_filename_sanitization(
        self, mock_secure_filename, mock_youtube
    ):
        """Test that filename is properly sanitized."""
        mock_youtube_instance = MagicMock()
        mock_youtube_instance.title = "Test/Video:With*Special|Chars?.mp4"
        mock_youtube.return_value = mock_youtube_instance

        mock_secure_filename.return_value = "Test_Video_With_Special_Chars_.mp4"

        mock_task = MagicMock()

        download = DownloadYoutube(
            url="https://www.youtube.com/watch?v=test", task=mock_task
        )

        # secure_filename should have been called
        mock_secure_filename.assert_called_once()
        # The filename should be sanitized
        assert "/" not in download.filename
        assert ":" not in download.filename

    @patch("services.download.plugins.youtube.YouTube")
    @patch("services.download.plugins.youtube.secure_filename")
    def test_download_youtube_filepath(self, mock_secure_filename, mock_youtube):
        """Test DownloadYoutube filepath construction."""
        mock_youtube_instance = MagicMock()
        mock_youtube_instance.title = "Test Video"
        mock_youtube.return_value = mock_youtube_instance

        mock_secure_filename.return_value = "Test_Video.mp4"

        mock_task = MagicMock()

        download = DownloadYoutube(
            url="https://www.youtube.com/watch?v=test", task=mock_task
        )

        # Check that filepath is constructed correctly (using default /media path)
        expected_path = Path("/media") / "youtube" / "Test_Video.mp4"
        assert download.filepath == expected_path

    @patch("services.download.plugins.youtube.YouTube")
    @patch("services.download.plugins.youtube.secure_filename")
    def test_download_youtube_start_no_audio_stream(
        self, mock_secure_filename, mock_youtube
    ):
        """Test DownloadYoutube start with no audio stream."""
        mock_youtube_instance = MagicMock()
        mock_youtube_instance.title = "Test Video"

        mock_video_stream = MagicMock()
        mock_youtube_instance.streams.get_highest_resolution.return_value = (
            mock_video_stream
        )
        mock_youtube_instance.streams.get_audio_only.return_value = []  # No audio streams

        mock_youtube.return_value = mock_youtube_instance
        mock_secure_filename.return_value = "Test_Video.mp4"

        mock_task = MagicMock()

        download = DownloadYoutube(
            url="https://www.youtube.com/watch?v=test", task=mock_task
        )

        # Should raise DownloadException
        with pytest.raises(DownloadException):
            download.start()
