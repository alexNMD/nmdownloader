from loguru import logger

from nmdownloader.config import app_settings
from nmdownloader.services.download.helpers import DownloadStatus

from ..helpers.exceptions import NotificationError
from ..helpers.format_size import format_size
from ..plugins.discord import DiscordAPI


class Notifier:
    def __init__(
        self, channel_id: int | None = None, thumbnail_url: str | None = None, message_id: int | None = None
    ) -> None:
        self.channel_id = channel_id or app_settings.discord.default_channel_id
        self.message_id = message_id
        self.thumbnail_url = thumbnail_url
        self.status_message_id = None
        # TODO: piste avec les medias name pour fetch la thumbnail

    def throw(
        self,
        title: str,
        status: DownloadStatus,
        description: str | None = None,
        thumbnail: str | None = None,
        total_size: int | None = None,
    ) -> None:
        embed_payload = {
            "title": title,
            "description": description,
            "color": status.value,
            "fields": [{"name": "Status", "value": status.name}],
            "thumbnail": thumbnail,
        }
        if total_size:
            embed_payload["fields"].append({"name": "Total Size", "value": format_size(total_size)})

        logger.info(f"{title} => {status.name}")

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
