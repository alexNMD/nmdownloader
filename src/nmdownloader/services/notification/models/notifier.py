from typing import TYPE_CHECKING, Any

from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.services.download.helpers import DownloadStatus

from ..helpers.exceptions import NotificationError
from ..helpers.format_size import format_size
from ..plugins.discord import DiscordAPI

if TYPE_CHECKING:
    from nmdownloader.services.download.models import DownloadBase


class Notifier:
    def __init__(
        self, channel_id: int | None = None, thumbnail_url: str | None = None, message_id: int | None = None
    ) -> None:
        self.channel_id = channel_id or app_settings.discord.default_channel_id
        self.message_id = message_id
        self.thumbnail_url = thumbnail_url
        # TODO: piste avec les medias name pour fetch la thumbnail
        self.status_message_id = None

    def throw(self, status: DownloadStatus, download: DownloadBase, **kwargs) -> None:
        embed_payload = self._build_embed(download=download, status=status, **kwargs)
        logger.info(embed_payload)

        try:
            if self.status_message_id:
                DiscordAPI.edit_embed(message_id=self.status_message_id, channel_id=self.channel_id, **embed_payload)
                return

            self.status_message_id = (
                DiscordAPI.reply_with_embed(message_id=self.message_id, channel_id=self.channel_id, **embed_payload)
                if self.message_id
                else DiscordAPI.send_embed(channel_id=self.channel_id, **embed_payload)
            )
        except NotificationError as notification_error:
            logger.error(f"Notification Failed: {notification_error}")
            return

    @classmethod
    def _build_embed(cls, download: DownloadBase, status: DownloadStatus, **kwargs) -> dict[str, Any]:
        embed_payload = {
            "title": download.filepath.name if hasattr(download, "filepath") else download.__class__.__name__,
            "color": status.value,
            "fields": [{"name": "Status", "value": status.name}],
            "thumbnail": getattr(download, "thumbnail", None),
        }

        if total_size := getattr(download, "total_size", None) is not None:
            embed_payload["fields"].append({"name": "Total Size", "value": format_size(total_size)})

        return {**embed_payload, **kwargs}
