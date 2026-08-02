"""Unit tests for services/discord module."""

from unittest.mock import MagicMock, patch


class TestDiscordAPI:
    """Tests for DiscordAPI class."""

    @patch("nmdownloader.services.discord.models.api.requests")
    def test_discord_api_build_embed_with_thumbnail(self, mock_requests: MagicMock) -> None:
        """Test _build_embed method with thumbnail parameter."""
        from nmdownloader.services.discord.models.api import DiscordAPI

        result = DiscordAPI._build_embed(
            title="Test Title",
            color=0x00FF00,
            description="Test Description",
            fields=[{"name": "Field1", "value": "Value1"}],
            thumbnail="https://example.com/thumbnail.jpg",
        )

        assert result["title"] == "Test Title"
        assert result["color"] == 0x00FF00
        assert result["description"] == "Test Description"
        assert result["fields"] == [{"name": "Field1", "value": "Value1", "inline": True}]
        assert result["thumbnail"] == {"url": "https://example.com/thumbnail.jpg"}
        assert result["footer"] == {"text": "NMDownloader"}
        assert "timestamp" in result

    @patch("nmdownloader.services.discord.models.api.requests")
    def test_discord_api_build_embed_without_thumbnail(self, mock_requests: MagicMock) -> None:
        """Test _build_embed method without thumbnail parameter."""
        from nmdownloader.services.discord.models.api import DiscordAPI

        result = DiscordAPI._build_embed(title="Test Title", color=0x00FF00, description="Test Description")

        assert result["title"] == "Test Title"
        assert result["color"] == 0x00FF00
        assert result["description"] == "Test Description"
        assert "thumbnail" not in result
        assert result["footer"] == {"text": "NMDownloader"}

    @patch("nmdownloader.services.discord.models.api.requests")
    def test_discord_api_build_embed_with_none_thumbnail(self, mock_requests: MagicMock) -> None:
        """Test _build_embed method with None thumbnail."""
        from nmdownloader.services.discord.models.api import DiscordAPI

        result = DiscordAPI._build_embed(title="Test Title", color=0x00FF00, thumbnail=None)

        assert "thumbnail" not in result

    @patch("nmdownloader.services.discord.models.api.requests")
    def test_discord_api_build_embed_minimal(self, mock_requests: MagicMock) -> None:
        """Test _build_embed method with minimal parameters."""
        from nmdownloader.services.discord.models.api import DiscordAPI

        result = DiscordAPI._build_embed(title="Test Title", color=0x00FF00)

        assert result["title"] == "Test Title"
        assert result["color"] == 0x00FF00
        assert "description" not in result
        assert "fields" not in result
        assert "thumbnail" not in result

    @patch("nmdownloader.services.discord.models.api.requests")
    def test_discord_api_send_embed_with_thumbnail(self, mock_requests: MagicMock) -> None:
        """Test send_embed method includes thumbnail in embed."""
        from nmdownloader.services.discord.models.api import DiscordAPI

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 12345}
        mock_response.raise_for_status.return_value = None
        mock_requests.request.return_value = mock_response

        with patch.object(DiscordAPI, "_build_embed") as mock_build_embed:
            mock_build_embed.return_value = {
                "title": "Test",
                "color": 0x00FF00,
                "timestamp": "2024-01-01T00:00:00",
                "footer": {"text": "NMDownloader"},
                "thumbnail": {"url": "https://example.com/thumbnail.jpg"},
            }

            result = DiscordAPI.send_embed(
                channel_id=123, title="Test Title", color=0x00FF00, thumbnail="https://example.com/thumbnail.jpg"
            )

            assert result == 12345
            mock_build_embed.assert_called_once()
            call_kwargs = mock_build_embed.call_args[1]
            assert call_kwargs["thumbnail"] == "https://example.com/thumbnail.jpg"

            mock_requests.request.assert_called_once()
            request_call_kwargs = mock_requests.request.call_args[1]
            assert "embeds" in request_call_kwargs["json"]
            assert len(request_call_kwargs["json"]["embeds"]) == 1

    @patch("nmdownloader.services.discord.models.api.requests")
    def test_discord_api_reply_with_embed_with_thumbnail(self, mock_requests: MagicMock) -> None:
        """Test reply_with_embed method includes thumbnail in embed."""
        from nmdownloader.services.discord.models.api import DiscordAPI

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 12345}
        mock_response.raise_for_status.return_value = None
        mock_requests.request.return_value = mock_response

        with patch.object(DiscordAPI, "_build_embed") as mock_build_embed:
            mock_build_embed.return_value = {
                "title": "Test",
                "color": 0x00FF00,
                "timestamp": "2024-01-01T00:00:00",
                "footer": {"text": "NMDownloader"},
                "thumbnail": {"url": "https://example.com/thumbnail.jpg"},
            }

            result = DiscordAPI.reply_with_embed(
                channel_id=123,
                message_id=456,
                title="Test Title",
                color=0x00FF00,
                thumbnail="https://example.com/thumbnail.jpg",
            )

            assert result == 12345
            mock_build_embed.assert_called_once()
            call_kwargs = mock_build_embed.call_args[1]
            assert call_kwargs["thumbnail"] == "https://example.com/thumbnail.jpg"

            mock_requests.request.assert_called_once()
            request_call_kwargs = mock_requests.request.call_args[1]
            assert "embeds" in request_call_kwargs["json"]
            assert "message_reference" in request_call_kwargs["json"]

    @patch("nmdownloader.services.discord.models.api.requests")
    def test_discord_api_edit_embed_with_thumbnail(self, mock_requests: MagicMock) -> None:
        """Test edit_embed method includes thumbnail in embed."""
        from nmdownloader.services.discord.models.api import DiscordAPI

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 12345}
        mock_response.raise_for_status.return_value = None
        mock_requests.request.return_value = mock_response

        with patch.object(DiscordAPI, "_build_embed") as mock_build_embed:
            mock_build_embed.return_value = {
                "title": "Test",
                "color": 0x00FF00,
                "timestamp": "2024-01-01T00:00:00",
                "footer": {"text": "NMDownloader"},
                "thumbnail": {"url": "https://example.com/thumbnail.jpg"},
            }

            result = DiscordAPI.edit_embed(
                channel_id=123,
                message_id=456,
                title="Test Title",
                color=0x00FF00,
                thumbnail="https://example.com/thumbnail.jpg",
            )

            assert result == 12345
            mock_build_embed.assert_called_once()
            call_kwargs = mock_build_embed.call_args[1]
            assert call_kwargs["thumbnail"] == "https://example.com/thumbnail.jpg"

            mock_requests.request.assert_called_once()
            request_call_args = mock_requests.request.call_args
            assert "channels/123/messages/456" in str(request_call_args)
            assert request_call_args[1]["method"] == "PATCH"
