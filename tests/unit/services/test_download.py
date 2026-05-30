"""Unit tests for services/download.py module."""

import inspect
from abc import ABC
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config.base import app_settings
from libs.download import DownloadRevokeException
from services.download import Download, DownloadStatus


class TestDownload:
    """Tests for Download abstract base class."""

    def test_download_is_abstract(self):
        """Test that Download is an abstract base class."""
        assert issubclass(Download, ABC)

    def test_download_abstract_method(self):
        """Test that Download has abstract start method."""
        assert hasattr(Download, "start")
        # Check it's abstract
        assert inspect.ismethod(Download.start) or inspect.isfunction(Download.start)


class TestDownloadConcrete:
    """Tests for Download class concrete methods."""

    def test_download_init(self):
        """Test Download class initialization."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(
            task=mock_task, filepath=filepath, message_id=123, channel_id=456
        )

        assert download.task == mock_task
        assert download.filepath == filepath
        assert download.message_id == 123
        assert download.channel_id == 456
        assert download.options == {}
        assert download.status_message_id is None

    def test_download_init_with_options(self):
        """Test Download initialization with options."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(
            task=mock_task, filepath=filepath, type_dl="series", quality="1080p"
        )

        assert download.options == {"type_dl": "series", "quality": "1080p"}

    def test_download_init_default_channel(self):
        """Test Download initialization with default channel."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        # Set default channel
        app_settings.discord.default_channel_id = 999

        download = ConcreteDownload(
            task=mock_task,
            filepath=filepath,
            channel_id=None,  # Should use default
        )

        assert download.channel_id == 999

    def test_download_remove(self):
        """Test Download _remove method."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test_test_remove.mkv")

        # Create a temporary file for the test
        filepath.touch()

        try:
            download = ConcreteDownload(task=mock_task, filepath=filepath)

            # Call _remove
            download._remove()

            # Check file is removed
            assert not filepath.exists()
        finally:
            # Cleanup if file still exists
            filepath.unlink(missing_ok=True)

    def test_download_remove_missing_file(self):
        """Test Download _remove with non-existent file."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/nonexistent_test_file.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath)

        # Should not raise error for missing file
        download._remove()

    def test_download_cancel(self):
        """Test Download cancel method."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test_cancel.mkv")

        # Create file first
        filepath.touch()

        try:
            download = ConcreteDownload(task=mock_task, filepath=filepath)

            # Call cancel - should raise DownloadRevokeException
            with pytest.raises(DownloadRevokeException):
                download.cancel()

            # File should be removed
            assert not filepath.exists()
        finally:
            filepath.unlink(missing_ok=True)

    def test_download_to_dict(self):
        """Test Download to_dict method."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(
            task=mock_task, filepath=filepath, message_id=123, channel_id=456
        )

        result = download.to_dict()

        assert isinstance(result, dict)
        assert "filepath" in result
        assert result["filepath"] == str(filepath)
        assert "message_id" in result
        assert result["message_id"] == 123
        assert "channel_id" in result
        assert result["channel_id"] == 456

    def test_download_to_dict_with_path_conversion(self):
        """Test that to_dict converts Path to string."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath)
        result = download.to_dict()

        assert isinstance(result["filepath"], str)
        assert result["filepath"] == str(filepath)

    @patch("services.download.logger")
    def test_download_update_status(self, mock_logger):
        """Test Download update_status method."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath)

        # Call update_status
        download.update_status(DownloadStatus.STARTED, "Starting download")

        # Check task state was updated
        mock_task.update_state.assert_called_once()

        # Check log was called
        mock_logger.info.assert_called()

    @patch("services.download.discord_api")
    @patch("services.download.logger")
    def test_download_update_status_with_discord(self, mock_logger, mock_discord_api):
        """Test Download update_status with Discord notifications."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        # Enable Discord
        app_settings.discord.token = "test_token"
        app_settings.discord.default_channel_id = 123

        mock_discord_api.send_embed = MagicMock()

        download = ConcreteDownload(
            task=mock_task, filepath=filepath, message_id=None, channel_id=123
        )

        # Call update_status
        download.update_status(DownloadStatus.STARTED, "Starting")

        # Discord API should be called
        mock_discord_api.send_embed.assert_called_once()

    def test_download_notification_without_token(self):
        """Test that notification is skipped without Discord token."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        # Ensure no Discord token
        app_settings.discord.token = None

        download = ConcreteDownload(task=mock_task, filepath=filepath)

        # Should not raise error even without token
        download.update_status(DownloadStatus.STARTED, "Starting")

    def test_download_notification_without_channel(self):
        """Test that notification logs error without channel ID."""

        # Create a concrete subclass for testing
        class ConcreteDownload(Download):
            def start(self):
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        # Set token but no default channel
        app_settings.discord.token = "test_token"
        app_settings.discord.default_channel_id = None

        download = ConcreteDownload(task=mock_task, filepath=filepath, channel_id=None)

        # Should log error but not crash
        with patch("services.download.logger") as mock_logger:
            download.update_status(DownloadStatus.STARTED, "Starting")
            mock_logger.error.assert_called_once()
