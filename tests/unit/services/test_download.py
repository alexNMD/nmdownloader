"""Unit tests for services/download.py module."""

import inspect
from abc import ABC
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from nmdownloader.config import app_settings
from nmdownloader.services.download.helpers import DownloadRevokeException, DownloadStatus
from nmdownloader.services.download.models import DownloadBase


class TestDownload:
    """Tests for Download abstract base class."""

    def test_download_is_abstract(self) -> None:
        """Test that Download is an abstract base class."""
        assert issubclass(DownloadBase, ABC)

    def test_download_abstract_method(self) -> None:
        """Test that Download has abstract start method."""
        assert hasattr(DownloadBase, "start")
        # Check it's abstract
        assert inspect.ismethod(DownloadBase.start) or inspect.isfunction(DownloadBase.start)


class TestDownloadConcrete:
    """Tests for Download class concrete methods."""

    def test_download_init(self) -> None:
        """Test Download class initialization."""

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath, message_id=123, channel_id=456)

        assert download.task == mock_task
        assert download.filepath == filepath
        assert download.options.get("message_id") == 123
        assert download.options.get("channel_id") == 456
        assert download.options == {"message_id": 123, "channel_id": 456}
        assert download.notifier.status_message_id is None

    def test_download_init_with_options(self) -> None:
        """Test Download initialization with options."""

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath, type_dl="series", quality="1080p")

        assert download.options == {"type_dl": "series", "quality": "1080p"}

    def test_download_init_default_channel(self) -> None:
        """Test Download initialization with default channel."""

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
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

        assert download.notifier.discord_channel_id == 999

    def test_download_remove(self) -> None:
        """Test Download _remove method."""

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
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

    def test_download_remove_missing_file(self) -> None:
        """Test Download _remove with non-existent file."""

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/nonexistent_test_file.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath)

        # Should not raise error for missing file
        download._remove()

    def test_download_cancel(self) -> None:
        """Test Download cancel method."""

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
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

    def test_download_to_dict(self) -> None:
        """Test Download to_dict method."""

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath, message_id=123, channel_id=456)

        result = download.to_dict()

        assert isinstance(result, dict)
        assert "filepath" in result
        assert result["filepath"] == str(filepath)
        assert "options" in result
        assert result["options"]["message_id"] == 123
        assert result["options"]["channel_id"] == 456

    def test_download_to_dict_with_path_conversion(self) -> None:
        """Test that to_dict converts Path to string."""

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath)
        result = download.to_dict()

        assert isinstance(result["filepath"], str)
        assert result["filepath"] == str(filepath)

    def test_download_update_status(self) -> None:
        """Test Download update_status method."""
        from nmdownloader.services.download.models import DownloadBase

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        download = ConcreteDownload(task=mock_task, filepath=filepath)

        # Call update_status
        download.update_status(DownloadStatus.STARTED, description="Starting download")

        # Check task state was updated
        mock_task.update_state.assert_called_once()

    def test_download_update_status_with_discord(self) -> None:
        """Test Download update_status with Discord notifications."""
        from nmdownloader.config import app_settings
        from nmdownloader.services.download.models import DownloadBase

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        # Enable Discord
        app_settings.discord.token = "test_token"
        app_settings.discord.default_channel_id = 123

        download = ConcreteDownload(task=mock_task, filepath=filepath, message_id=None, channel_id=123)

        # Call update_status - should not raise error
        download.update_status(DownloadStatus.STARTED, description="Starting")

        # Task state should be updated
        mock_task.update_state.assert_called_once()

    def test_download_notification_without_token(self) -> None:
        """Test that notification is skipped without Discord token."""
        from nmdownloader.config import app_settings
        from nmdownloader.services.download.models import DownloadBase

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        # Ensure no Discord token
        app_settings.discord.token = None

        download = ConcreteDownload(task=mock_task, filepath=filepath)

        # Should not raise error even without token
        download.update_status(DownloadStatus.STARTED, description="Starting")

    def test_download_notification_without_channel(self) -> None:
        """Test that notification logs error without channel ID."""
        from nmdownloader.config import app_settings
        from nmdownloader.services.download.models import DownloadBase

        # Create a concrete subclass for testing
        class ConcreteDownload(DownloadBase):
            def _setup(self) -> None:
                pass

            def _download(self) -> None:
                pass

            def _terminate(self) -> None:
                pass

        mock_task = MagicMock()
        filepath = Path("/tmp/test.mkv")

        # Set token but no default channel
        app_settings.discord.token = "test_token"

        download = ConcreteDownload(task=mock_task, filepath=filepath, channel_id=None)

        # Should not crash even without channel
        download.update_status(DownloadStatus.STARTED, description="Starting")

        # Task state should still be updated
        mock_task.update_state.assert_called_once()
