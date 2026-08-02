"""Unit tests for services/download/models/media.py module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from nmdownloader.services.download.models import DownloadMedia


class TestDownloadMedia:
    """Tests for DownloadMedia class."""

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail")
    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_media_init_with_thumbnail(
        self, mock_head: MagicMock, mock_get_thumbnail: MagicMock, mock_app_settings: MagicMock
    ) -> None:
        """Test DownloadMedia initialization sets thumbnail from TMDB."""
        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Series.S01E01.mkv"'}
        mock_head.return_value = mock_head_response

        mock_get_thumbnail.return_value = "https://image.tmdb.org/t/p/w200/test_poster.jpg"

        mock_task = MagicMock()

        # Create DownloadMedia instance
        download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

        # Assertions
        assert download.filename == "Test.Series.S01E01.mkv"
        assert download.thumbnail == "https://image.tmdb.org/t/p/w200/test_poster.jpg"
        assert download.type_dl == "series"
        assert download.base_download_path == Path("/tmp/media/series")

        # Check that TMDBApi.get_thumbnail was called
        mock_get_thumbnail.assert_called_once()

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail")
    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_media_init_film_thumbnail(
        self, mock_head: MagicMock, mock_get_thumbnail: MagicMock, mock_app_settings: MagicMock
    ) -> None:
        """Test DownloadMedia initialization for film sets correct type and thumbnail."""
        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Movie.2024.mkv"'}
        mock_head.return_value = mock_head_response

        mock_get_thumbnail.return_value = "https://image.tmdb.org/t/p/w200/movie_poster.jpg"

        mock_task = MagicMock()

        # Create DownloadMedia instance for a film
        download = DownloadMedia(url="https://example.com/movie.mkv", task=mock_task)

        # Assertions
        assert download.filename == "Test.Movie.2024.mkv"
        assert download.thumbnail == "https://image.tmdb.org/t/p/w200/movie_poster.jpg"
        assert download.type_dl == "films"
        assert download.base_download_path == Path("/tmp/media/films")

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail")
    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_media_init_no_thumbnail(
        self, mock_head: MagicMock, mock_get_thumbnail: MagicMock, mock_app_settings: MagicMock
    ) -> None:
        """Test DownloadMedia initialization when TMDB returns no thumbnail."""
        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Series.S01E01.mkv"'}
        mock_head.return_value = mock_head_response

        mock_get_thumbnail.return_value = None

        mock_task = MagicMock()

        # Create DownloadMedia instance
        download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

        # Assertions
        assert download.filename == "Test.Series.S01E01.mkv"
        assert download.thumbnail is None
        assert download.type_dl == "series"

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail")
    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_media_init_thumbnail_error(
        self, mock_head: MagicMock, mock_get_thumbnail: MagicMock, mock_app_settings: MagicMock
    ) -> None:
        """Test DownloadMedia initialization when TMDB API call fails."""
        import requests.exceptions

        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="Test.Series.S01E01.mkv"'}
        mock_head.return_value = mock_head_response

        mock_get_thumbnail.side_effect = requests.exceptions.RequestException("API Error")

        mock_task = MagicMock()

        # Create DownloadMedia instance - should not raise error
        download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

        # Assertions
        assert download.filename == "Test.Series.S01E01.mkv"
        assert download.thumbnail is None
        assert download.type_dl == "series"

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_media_get_media_name_series(self, mock_head: MagicMock, mock_app_settings: MagicMock) -> None:
        """Test _get_media_name for series filename."""
        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="My.Series.S01E01.mkv"'}
        mock_head.return_value = mock_head_response

        mock_task = MagicMock()

        # Create DownloadMedia instance
        download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

        # Call the method
        result = download._get_media_name()

        # Assertions
        assert result == "My.Series"

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_media_get_media_name_film(self, mock_head: MagicMock, mock_app_settings: MagicMock) -> None:
        """Test _get_media_name for film filename."""
        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="My.Movie.2024.mkv"'}
        mock_head.return_value = mock_head_response

        mock_task = MagicMock()

        # Create DownloadMedia instance
        download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

        # Call the method
        result = download._get_media_name()

        # Assertions
        assert result == "My.Movie"

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.requests.head")
    def test_download_media_get_media_name_simple(self, mock_head: MagicMock, mock_app_settings: MagicMock) -> None:
        """Test _get_media_name for simple filename."""
        # Setup mocks
        mock_app_settings.media_path = Path("/tmp/media")

        mock_head_response = MagicMock()
        mock_head_response.headers = {"Content-Disposition": 'attachment; filename="simple_file.mkv"'}
        mock_head.return_value = mock_head_response

        mock_task = MagicMock()

        # Create DownloadMedia instance
        download = DownloadMedia(url="https://example.com/test.mkv", task=mock_task)

        # Call the method
        result = download._get_media_name()

        # Assertions - should fall back to filename without extension
        assert result == "simple_file"

    @patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail")
    def test_download_media_get_thumbnail_static_method(self, mock_get_thumbnail: MagicMock) -> None:
        """Test _get_thumbnail class method."""
        from nmdownloader.services.download.models.media import DownloadMedia

        mock_get_thumbnail.return_value = "https://image.tmdb.org/t/p/w200/test.jpg"

        # Call the static method
        result = DownloadMedia._get_thumbnail(media_name="Test Movie")

        # Assertions
        assert result == "https://image.tmdb.org/t/p/w200/test.jpg"
        mock_get_thumbnail.assert_called_once_with(query="Test Movie")

    @patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail")
    def test_download_media_get_thumbnail_error_handling(self, mock_get_thumbnail: MagicMock) -> None:
        """Test _get_thumbnail class method error handling."""
        import requests.exceptions

        from nmdownloader.services.download.models.media import DownloadMedia

        mock_get_thumbnail.side_effect = requests.exceptions.RequestException("API Error")

        # Call the static method - should not raise error, just log and return None
        result = DownloadMedia._get_thumbnail(media_name="Test Movie")

        # Assertions
        assert result is None

    @patch("nmdownloader.services.download.models.media.TMDBApi.get_thumbnail")
    @patch("nmdownloader.services.download.models.media.logger")
    def test_download_media_get_thumbnail_http_error(
        self, mock_logger: MagicMock, mock_get_thumbnail: MagicMock
    ) -> None:
        """Test _get_thumbnail class method with HTTP error."""
        import requests.exceptions

        from nmdownloader.services.download.models.media import DownloadMedia

        # Create a mock HTTPError with a response attribute
        mock_error = requests.exceptions.HTTPError("Not Found")
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_error.response = mock_response

        mock_get_thumbnail.side_effect = mock_error

        # Call the static method - should not raise error, just log and return None
        result = DownloadMedia._get_thumbnail(media_name="Test Movie")

        # Assertions
        assert result is None
        mock_logger.error.assert_called_once()

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.Path")
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
                with (
                    patch("nmdownloader.services.download.models.base.DiscordAPI"),
                    patch("nmdownloader.services.download.models.base.logger"),
                ):
                    download._setup()

                # Check that update_status was called with STARTED
                mock_task.update_state.assert_called()
                # Check that mkdir was called on the destination directory
                mock_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("nmdownloader.services.download.models.media.app_settings")
    @patch("nmdownloader.services.download.models.media.Path")
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

                # Call _terminate - mock DiscordAPI and logger to avoid side effects
                with (
                    patch("nmdownloader.services.download.models.base.DiscordAPI"),
                    patch("nmdownloader.services.download.models.base.logger"),
                ):
                    download._terminate()

                # Check that update_status was called
                assert mock_task.update_state.call_count >= 1
