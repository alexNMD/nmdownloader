"""Unit tests for services/tmdb module."""

from unittest.mock import MagicMock, patch

import pytest

from nmdownloader.services.notification import NotificationError


class TestTMDBApi:
    """Tests for TMDBApi class."""

    @patch("requests.request")
    def test_tmdb_api_call_success(self, mock_request: MagicMock) -> None:
        """Test TMDBApi._call_and_get_json with successful response."""
        from nmdownloader.services.notification.plugins.tmdb import TMDBApi

        # Mock API_TOKEN to avoid auth error
        TMDBApi.API_TOKEN = "test_token"

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Call the method
        result = TMDBApi._call_and_get_json(endpoint="test/endpoint", method="GET")

        # Assertions
        assert result == {"key": "value"}
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "test/endpoint" in str(call_args)
        assert "Authorization" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

    @patch("requests.request")
    def test_tmdb_api_call_http_error(self, mock_request: MagicMock) -> None:
        """Test TMDBApi._call_and_get_json with HTTP error."""
        import requests.exceptions

        from nmdownloader.services.notification.plugins.tmdb import TMDBApi

        # Mock API_TOKEN to avoid auth error
        TMDBApi.API_TOKEN = "test_token"

        # Setup mock to raise HTTPError
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_request.return_value = mock_response

        # Should raise NotificationError (wrapped HTTPError)
        with pytest.raises(NotificationError):  # NotificationError wraps HTTPError
            TMDBApi._call_and_get_json(endpoint="test/endpoint", method="GET")

    @patch("requests.request")
    def test_tmdb_api_get_results(self, mock_request: MagicMock) -> None:
        """Test TMDBApi.get_results method."""
        from nmdownloader.services.notification.plugins.tmdb import TMDBApi

        # Mock API_TOKEN to avoid auth error
        TMDBApi.API_TOKEN = "test_token"

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"id": 123, "title": "Test Movie"}]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Call the method
        result = TMDBApi.get_results(endpoint="search/multi", params={"query": "Test Movie", "page": "1"})

        # Assertions
        assert result == [{"id": 123, "title": "Test Movie"}]
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "search/multi" in str(call_args)
        assert call_args[1]["params"]["query"] == "Test Movie"
        assert call_args[1]["params"]["page"] == "1"

    @patch("nmdownloader.services.notification.plugins.tmdb.TMDBApi._call_and_get_json")
    def test_tmdb_api_get_thumbnail_success(self, mock_call: MagicMock) -> None:
        """Test TMDBApi.get_thumbnail with successful response."""
        from nmdownloader.services.notification.plugins.tmdb import TMDBApi

        # Setup mock response with poster_path
        mock_call.return_value = {
            "results": [{"id": 123, "title": "Test Movie", "poster_path": "/path/to/poster.jpg", "popularity": 100}]
        }

        # Call the method
        result = TMDBApi.get_thumbnail(query="Test Movie")

        # Assertions
        assert result == "https://image.tmdb.org/t/p/w200/path/to/poster.jpg"
        # Called once per language in app_settings.tmdb.languages_iso639_1
        assert mock_call.call_count == 2
        # Check that both calls have the correct base params
        for call in mock_call.call_args_list:
            assert call[1]["endpoint"] == "search/multi"
            assert call[1]["method"] == "GET"
            assert "page" in call[1]["params"]
            assert "include_adult" in call[1]["params"]
            assert "query" in call[1]["params"]

    @patch("nmdownloader.services.notification.plugins.tmdb.TMDBApi._call_and_get_json")
    def test_tmdb_api_get_thumbnail_no_results(self, mock_call: MagicMock) -> None:
        """Test TMDBApi.get_thumbnail with no results."""
        from nmdownloader.services.notification.plugins.tmdb import TMDBApi

        # Setup mock response with no results
        mock_call.return_value = {"results": []}

        # Call the method
        result = TMDBApi.get_thumbnail(query="Non Existent Movie")

        # Should return None
        assert result is None

    @patch("nmdownloader.services.notification.plugins.tmdb.TMDBApi._call_and_get_json")
    def test_tmdb_api_get_thumbnail_no_poster_path(self, mock_call: MagicMock) -> None:
        """Test TMDBApi.get_thumbnail when result has no poster_path."""
        from nmdownloader.services.notification.plugins.tmdb import TMDBApi

        # Setup mock response without poster_path
        mock_call.return_value = {"results": [{"id": 123, "title": "Test Movie"}]}

        # Call the method
        result = TMDBApi.get_thumbnail(query="Test Movie")

        # Should return None
        assert result is None

    @patch("nmdownloader.services.notification.plugins.tmdb.TMDBApi._call_and_get_json")
    def test_tmdb_api_get_thumbnail_invalid_results(self, mock_call: MagicMock) -> None:
        """Test TMDBApi.get_thumbnail with invalid results format."""
        from nmdownloader.services.notification.plugins.tmdb import TMDBApi

        # Setup mock response with invalid results (not a list)
        mock_call.return_value = {"results": "invalid"}

        # Call the method
        result = TMDBApi.get_thumbnail(query="Test Movie")

        # Should return None
        assert result is None
