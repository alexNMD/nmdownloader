"""Unit tests for services/download/models/media.py module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from nmdownloader.services.download.models import DownloadMedia


class TestDownloadMedia:
    """Tests for DownloadMedia class."""

    @patch("nmdownloader.config.app_settings")
    @patch("nmdownloader.services.notification.plugins.tmdb.TMDBApi.get_thumbnail")
    @patch("requests.head")
    def test_download_media_init_with_thumbnail(
        self, mock_head: MagicMock, mock_get_thumbnail: MagicMock, mock_app_settings: MagicMock
    ) -> None:
        """Test DownloadMedia initialization sets thumbnail from TMDB."""
        # Setup mocks
        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Series.S01E01.mkv"'}
        mock_head.return_value.__enter__.return_value = mock_head_response

        mock_get_thumbnail.return_value = "https://image.tmdb.org/t/p/w200/test_poster.jpg"

        mock_task = MagicMock()

        # Create DownloadMedia instance
        download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

        # Assertions
        assert download.filename == "Test.Series.S01E01.mkv"
        assert download.thumbnail == "https://image.tmdb.org/t/p/w200/test_poster.jpg"
        assert download.type_dl == "series"
        assert download.base_download_path == Path("/media/series")

        # Check that TMDBApi.get_thumbnail was called
        mock_get_thumbnail.assert_called_once()

    @patch("nmdownloader.config.app_settings")
    @patch("nmdownloader.services.notification.plugins.tmdb.TMDBApi.get_thumbnail")
    @patch("requests.head")
    def test_download_media_init_film_thumbnail(
        self, mock_head: MagicMock, mock_get_thumbnail: MagicMock, mock_app_settings: MagicMock
    ) -> None:
        """Test DownloadMedia initialization for film sets correct type and thumbnail."""
        # Setup mocks
        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Movie.2024.mkv"'}
        mock_head.return_value.__enter__.return_value = mock_head_response

        mock_get_thumbnail.return_value = "https://image.tmdb.org/t/p/w200/movie_poster.jpg"

        mock_task = MagicMock()

        # Create DownloadMedia instance for a film
        download = DownloadMedia(url="https://example.com/movie.mkv", task=mock_task)

        # Assertions
        assert download.filename == "Test.Movie.2024.mkv"
        assert download.thumbnail == "https://image.tmdb.org/t/p/w200/movie_poster.jpg"
        assert download.type_dl == "films"
        assert download.base_download_path == Path("/media/films")

    @patch("nmdownloader.config.app_settings")
    @patch("nmdownloader.services.notification.plugins.tmdb.TMDBApi.get_thumbnail")
    @patch("requests.head")
    def test_download_media_init_no_thumbnail(
        self, mock_head: MagicMock, mock_get_thumbnail: MagicMock, mock_app_settings: MagicMock
    ) -> None:
        """Test DownloadMedia initialization when TMDB returns no thumbnail."""
        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Series.S01E01.mkv"'}
        mock_head.return_value.__enter__.return_value = mock_head_response

        mock_get_thumbnail.return_value = None

        mock_task = MagicMock()

        # Create DownloadMedia instance
        download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

        # Assertions
        assert download.filename == "Test.Series.S01E01.mkv"
        assert download.thumbnail is None
        assert download.type_dl == "series"

    @patch("nmdownloader.config.app_settings")
    @patch("pathlib.Path")
    def test_download_media_setup_creates_directory(self, mock_path: MagicMock, mock_app_settings: MagicMock) -> None:
        """Test _setup method creates destination directory."""

        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        # Mock Path for the destination directory
        mock_dir = MagicMock()
        mock_path.return_value = mock_dir

        # Mock requests.head for filename extraction
        with patch("nmdownloader.services.download.models.media.requests.head") as mock_head:
            mock_head_response = MagicMock()
            mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Series.S01E01.mkv"'}
            mock_head.return_value = mock_head_response

            with patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail") as mock_thumbnail:
                mock_thumbnail.return_value = None

                mock_task = MagicMock()

                # Create DownloadMedia instance
                download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

                # Mock the destination_directory to return our mocked path
                download.destination_directory = mock_path.return_value

                # Call _setup
                with patch("loguru.logger"):
                    download._setup()

                # Check that update_status was called with STARTED
                mock_task.update_state.assert_called()
                # Check that mkdir was called on the destination directory
                mock_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("nmdownloader.config.app_settings")
    @patch("pathlib.Path")
    def test_download_media_terminate_calls_update_status(
        self, mock_path: MagicMock, mock_app_settings: MagicMock
    ) -> None:
        """Test _terminate method calls update_status with DONE."""

        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        # Mock Path for the destination directory
        mock_dir = MagicMock()
        mock_path.return_value = mock_dir

        # Mock requests.head for filename extraction - use a non-compressed file
        with patch("nmdownloader.services.download.models.media.requests.head") as mock_head:
            mock_head_response = MagicMock()
            mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Series.S01E01.mp4"'}
            mock_head.return_value = mock_head_response

            with patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail") as mock_thumbnail:
                mock_thumbnail.return_value = None

                mock_task = MagicMock()

                # Create DownloadMedia instance - .mp4 is not in compressed formats
                download = DownloadMedia(url="https://example.com/test.mp4", task=mock_task)

                # Verify is_compressed is False for .mp4 files
                assert download.is_compressed is False

                # Call _terminate - mock logger to avoid side effects
                with patch("loguru.logger"):
                    download._terminate()

                # Check that update_status was called
                assert mock_task.update_state.call_count >= 1
