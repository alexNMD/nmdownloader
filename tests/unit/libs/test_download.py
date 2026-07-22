"""Unit tests for libs/download.py module."""

from unittest.mock import MagicMock, patch

from celery.exceptions import Ignore

from services.download.helpers import DownloadStatus


class TestDownloadStatus:
    """Tests for DownloadStatus enum."""

    def test_download_status_enum_values(self) -> None:
        """Test that DownloadStatus has expected values."""
        assert hasattr(DownloadStatus, "STARTED")
        assert hasattr(DownloadStatus, "RUNNING")
        assert hasattr(DownloadStatus, "DONE")
        assert hasattr(DownloadStatus, "ERROR")
        assert hasattr(DownloadStatus, "CANCELED")

    def test_download_status_hex_values(self) -> None:
        """Test that DownloadStatus values are hex color codes."""
        # These are the expected hex values (converted to int)
        assert DownloadStatus.STARTED.value == int("e8f30b", 16)
        assert DownloadStatus.RUNNING.value == int("f3ad0b", 16)
        assert DownloadStatus.DONE.value == int("0dba2f", 16)
        assert DownloadStatus.ERROR.value == int("f63106", 16)
        assert DownloadStatus.CANCELED.value == int("510666", 16)

    def test_download_status_names(self) -> None:
        """Test DownloadStatus enum member names."""
        assert DownloadStatus.STARTED.name == "STARTED"
        assert DownloadStatus.RUNNING.name == "RUNNING"
        assert DownloadStatus.DONE.name == "DONE"
        assert DownloadStatus.ERROR.name == "ERROR"
        assert DownloadStatus.CANCELED.name == "CANCELED"


class TestDownloadException:
    """Tests for DownloadException class."""

    def test_download_exception_inheritance(self) -> None:
        """Test that DownloadException inherits from Exception."""
        from services.download.helpers.exceptions import DownloadError

        assert issubclass(DownloadError, Exception)

    def test_download_exception_init(self) -> None:
        """Test DownloadException initialization."""
        from services.download.helpers.exceptions import DownloadError

        mock_download = MagicMock()
        mock_download.update_status = MagicMock()

        message = "Test error message"
        exception = DownloadError(mock_download, message)

        assert str(exception) == message
        mock_download.update_status.assert_called_once()

        # Check that it was called with ERROR status
        from services.download.helpers import DownloadStatus

        call_args = mock_download.update_status.call_args
        assert call_args[0][0] == DownloadStatus.ERROR
        assert call_args[0][1] == message

    def test_download_exception_logs_error(self) -> None:
        """Test that DownloadException logs the error."""
        mock_download = MagicMock()
        message = "Test error"

        with patch("services.download.helpers.exceptions.logger") as mock_logger:
            from services.download.helpers.exceptions import DownloadError

            DownloadError(mock_download, message)

        mock_logger.error.assert_called_once_with(message)


class TestDownloadRevokeException:
    """Tests for DownloadRevokeException class."""

    def test_download_revoke_exception_inheritance(self) -> None:
        """Test that DownloadRevokeException inherits from Ignore."""
        from services.download.helpers.exceptions import DownloadRevokeException

        assert issubclass(DownloadRevokeException, Ignore)

    def test_download_revoke_exception_default_message(self) -> None:
        """Test DownloadRevokeException with default message."""
        from services.download.helpers.exceptions import DownloadRevokeException

        mock_download = MagicMock()
        mock_download.update_status = MagicMock()

        exception = DownloadRevokeException(mock_download)

        assert str(exception) == "Canceled by User"
        mock_download.update_status.assert_called_once()

        # Check that it was called with CANCELED status
        from services.download.helpers import DownloadStatus

        call_args = mock_download.update_status.call_args
        assert call_args[0][0] == DownloadStatus.CANCELED
        assert call_args[0][1] == "Canceled by User"

    def test_download_revoke_exception_custom_message(self) -> None:
        """Test DownloadRevokeException with custom message."""
        from services.download.helpers.exceptions import DownloadRevokeException

        mock_download = MagicMock()
        mock_download.update_status = MagicMock()

        custom_message = "Custom cancel message"
        exception = DownloadRevokeException(mock_download, custom_message)

        assert str(exception) == custom_message
        mock_download.update_status.assert_called_once()

        # Check that it was called with CANCELED status
        from services.download.helpers import DownloadStatus

        call_args = mock_download.update_status.call_args
        assert call_args[0][0] == DownloadStatus.CANCELED
        assert call_args[0][1] == custom_message

    def test_download_revoke_exception_logs_info(self) -> None:
        """Test that DownloadRevokeException logs at info level."""
        mock_download = MagicMock()

        with patch("services.download.helpers.exceptions.logger") as mock_logger:
            from services.download.helpers.exceptions import DownloadRevokeException

            DownloadRevokeException(mock_download)

        mock_logger.info.assert_called_once_with("Download Canceled")
