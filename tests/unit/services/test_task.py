"""Unit tests for libs/task.py module."""

from unittest.mock import MagicMock, patch

from nmdownloader.services.download.helpers.task import get_task_result


class TestGetTaskResult:
    """Tests for get_task_result function."""

    def test_get_task_result_function_exists(self) -> None:
        """Test that get_task_result function exists."""
        assert callable(get_task_result)

    @patch("nmdownloader.services.download.helpers.task.AsyncResult")
    def test_get_task_result_with_successful_task(self, mock_async_result: MagicMock) -> None:
        """Test get_task_result with a successful task."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.successful.return_value = True
        mock_result.status = "SUCCESS"
        mock_result.info = {"key": "value"}
        mock_async_result.return_value = mock_result

        result = get_task_result("task-id-123")

        assert result["successful"] is True
        assert result["status"] == "SUCCESS"
        assert result["info"] == {"key": "value"}

    @patch("nmdownloader.services.download.helpers.task.celery_app")
    @patch("nmdownloader.services.download.helpers.task.AsyncResult")
    def test_get_task_result_with_failed_task(self, mock_async_result: MagicMock, mock_celery_app: MagicMock) -> None:
        """Test get_task_result with a failed task."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.successful.return_value = False
        mock_result.status = "FAILURE"
        mock_result.info = Exception("Task failed")
        mock_async_result.return_value = mock_result

        result = get_task_result("task-id-123")

        assert result["successful"] is False
        assert result["status"] == "FAILURE"
        # Exception should be converted to string
        assert isinstance(result["info"], str)
        assert "Task failed" in result["info"]

    @patch("nmdownloader.services.download.helpers.task.celery_app")
    @patch("nmdownloader.services.download.helpers.task.AsyncResult")
    def test_get_task_result_returns_dict(self, mock_async_result: MagicMock, mock_celery_app: MagicMock) -> None:
        """Test that get_task_result returns a dictionary."""
        mock_result = MagicMock()
        mock_result.successful.return_value = True
        mock_result.status = "PENDING"
        mock_result.info = None
        mock_async_result.return_value = mock_result

        result = get_task_result("task-id-123")

        assert isinstance(result, dict)
        assert "successful" in result
        assert "status" in result
        assert "info" in result

    @patch("nmdownloader.services.download.helpers.task.celery_app")
    @patch("nmdownloader.services.download.helpers.task.AsyncResult")
    def test_get_task_result_with_complex_info(self, mock_async_result: MagicMock, mock_celery_app: MagicMock) -> None:
        """Test get_task_result with complex info object."""
        # Setup mock with complex info
        mock_result = MagicMock()
        mock_result.successful.return_value = True
        mock_result.status = "SUCCESS"
        mock_result.info = {"download": {"filename": "test.mkv", "size": 1024, "progress": 50}}
        mock_async_result.return_value = mock_result

        result = get_task_result("task-id-123")

        assert result["successful"] is True
        assert result["info"]["download"]["filename"] == "test.mkv"
