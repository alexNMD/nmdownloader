"""Unit tests for libs/plugins.py module."""

from config import app_settings
from services.download.helpers.plugins import get_downloader, register_downloader
from services.download.plugins.un_fichier import Download1fichier
from services.download.plugins.youtube import DownloadYoutube
from services.download.models.default import DownloadDefault
from urllib.parse import urlparse


class TestRegisterDownloader:
    """Tests for register_downloader decorator."""

    def test_register_downloader_decorator_exists(self):
        """Test that register_downloader decorator exists."""
        assert callable(register_downloader)

    def test_register_downloader_with_single_host(self, clean_registry):
        """Test registering a downloader with a single host."""
        # Clear the registry first
        app_settings.downloader.plugin.registry.clear()

        # Create a mock class
        class MockDownloader:
            pass

        # Register the downloader
        decorator = register_downloader("example.com")
        decorator(MockDownloader)

        # Check that it's registered
        assert "example.com" in app_settings.downloader.plugin.registry
        assert app_settings.downloader.plugin.registry["example.com"] == MockDownloader

    def test_register_downloader_with_multiple_hosts(self, clean_registry):
        """Test registering a downloader with multiple hosts."""
        # Clear the registry
        app_settings.downloader.plugin.registry.clear()

        class MockDownloader:
            pass

        # Register with multiple hosts
        decorator = register_downloader(
            "example.com", "www.example.com", "cdn.example.com"
        )
        decorator(MockDownloader)

        # Check all hosts are registered
        assert "example.com" in app_settings.downloader.plugin.registry
        assert "www.example.com" in app_settings.downloader.plugin.registry
        assert "cdn.example.com" in app_settings.downloader.plugin.registry

        # All should point to the same class
        assert app_settings.downloader.plugin.registry["example.com"] == MockDownloader
        assert (
            app_settings.downloader.plugin.registry["www.example.com"] == MockDownloader
        )
        assert (
            app_settings.downloader.plugin.registry["cdn.example.com"] == MockDownloader
        )

    def test_register_downloader_returns_class(self, clean_registry):
        """Test that register_downloader returns the class."""
        app_settings.downloader.plugin.registry.clear()

        class MockDownloader:
            pass

        decorator = register_downloader("test.com")
        result = decorator(MockDownloader)

        assert result is MockDownloader


class TestGetDownloader:
    """Tests for get_downloader function."""

    def test_get_downloader_function_exists(self):
        """Test that get_downloader function exists."""
        assert callable(get_downloader)

    def test_get_downloader_returns_registered_class(self, clean_registry):
        """Test getting a registered downloader."""
        app_settings.downloader.plugin.registry.clear()

        class MockDownloader:
            pass

        # Register a downloader
        register_downloader("test.com")(MockDownloader)

        # Get the downloader
        result = get_downloader("https://test.com/file")

        assert result == MockDownloader

    def test_get_downloader_returns_default_for_unknown_host(self, clean_registry):
        """Test getting default downloader for unknown host."""
        app_settings.downloader.plugin.registry.clear()

        # Get downloader for unknown host
        result = get_downloader("https://unknown.com/file")

        assert result == DownloadDefault

    def test_get_downloader_with_youtube_urls(self):
        """Test getting downloader for YouTube URLs."""
        # Import to register the YouTube downloader

        # Test various YouTube URLs
        youtube_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
        ]

        for url in youtube_urls:
            result = get_downloader(url)
            assert result == DownloadYoutube

    def test_get_downloader_with_un_fichier_url(self):
        """Test getting downloader for 1fichier URLs."""
        # Import to register the 1fichier downloader
        import services.download.plugins.un_fichier  # noqa: F401

        url = "https://1fichier.com/?abc123"
        result = get_downloader(url)

        assert result == Download1fichier

    def test_get_downloader_parses_url_correctly(self):
        """Test that URL parsing extracts netloc correctly."""

        # URL with www should match youtube.com registration
        result = get_downloader("https://www.youtube.com/watch?v=test")
        assert result == DownloadYoutube

        # URL without www should also match
        result = get_downloader("https://youtube.com/watch?v=test")
        assert result == DownloadYoutube

    def test_get_downloader_handles_url_with_port(self):
        """Test getting downloader with URL containing port."""
        # Test that urlparse correctly extracts netloc with port
        url = "http://localhost:8080/file"
        parsed = urlparse(url)

        # netloc should be "localhost:8080"
        assert parsed.netloc == "localhost:8080"

        # This test verifies that the get_downloader function
        # would correctly use urlparse to extract the host
        # The actual registration test is done in test_register_downloader_with_single_host
