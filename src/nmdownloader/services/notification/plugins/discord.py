from datetime import UTC, datetime
from typing import NotRequired, TypedDict

from loguru import logger

from nmdownloader.config import app_settings

from ..helpers.constants import HttpVerb
from ..helpers.exceptions import NotificationError
from ..models.base import BaseNotification


class EmbedFieldPayload(TypedDict):
    name: str
    value: str
    inline: bool


class EmbedPayload(TypedDict):
    timestamp: str
    title: str
    color: int
    footer: dict[str, str]
    fields: NotRequired[list[dict[str, str | bool]]]
    description: NotRequired[str]
    thumbnail: NotRequired[dict[str, str]]


class DiscordAPI(BaseNotification):
    BASE_URL = app_settings.discord.api_url
    API_VERSION = app_settings.discord.api_version
    BEARER_SCHEMA = "Bot"
    API_TOKEN = app_settings.discord.token

    @classmethod
    def _send_and_get_message_id(cls, endpoint: str, channel_id: int | None, **kwargs) -> int:
        if not channel_id:
            raise NotificationError("DISCORD_DEFAULT_CHANNEL_ID not set. Unable to send notification")

        _channel_id = channel_id or app_settings.discord.default_channel_id
        response_json = cls._call_and_get_json(endpoint=f"channels/{_channel_id}/{endpoint}", **kwargs)

        if not (message_id := response_json.get("id")):
            raise NotificationError("Unable to retrieve message id from Discord API")

        return message_id

    @classmethod
    def _build_embed(
        cls,
        title: str,
        color: int,
        description: str | None = None,
        fields: list[dict[str, str]] | None = None,
        thumbnail: str | None = None,
    ) -> EmbedPayload:
        embed_payload: EmbedPayload = {
            "title": title,
            "color": color,
            "timestamp": datetime.now(UTC).isoformat(),
            "footer": {
                "text": "NMDownloader",
            },
        }
        if description:
            embed_payload["description"] = description
        if fields:
            embed_payload["fields"] = [
                {"name": field["name"], "value": field["value"], "inline": True} for field in fields
            ]
        if thumbnail:
            embed_payload["thumbnail"] = {"url": thumbnail}

        logger.info(f"embed sent: {embed_payload}")

        return embed_payload

    @classmethod
    def reply_with_embed(cls, message_id: int, channel_id: int | None, **kwargs) -> int:
        """
        Répond à un message dans un canal Discord avec un embed.
        :param channel_id: ID du canal où le message a été envoyé.
        :param message_id: ID du message auquel répondre.
        :param title: Le titre de l'embed.
        :param description: La description de l'embed.
        :param color: La couleur de l'embed (en hexadécimal).
        :return: La réponse de l'API Discord.
        """
        return cls._send_and_get_message_id(
            method=HttpVerb.POST,
            channel_id=channel_id,
            endpoint="messages",
            json={"embeds": [cls._build_embed(**kwargs)], "message_reference": {"message_id": message_id}},
        )

    @classmethod
    def send_embed(cls, channel_id: int | None = None, **kwargs) -> int:
        """
        Envoie un message dans un canal Discord avec un embed (sans répondre à un autre message).
        :param channel_id: ID du canal où envoyer le message.
        :param title: Le titre de l'embed.
        :param description: La description de l'embed.
        :param color: La couleur de l'embed (en hexadécimal ou entier).
        :return: La réponse de l'API Discord.
        """
        return cls._send_and_get_message_id(
            method=HttpVerb.POST,
            channel_id=channel_id,
            endpoint="messages",
            json={"embeds": [cls._build_embed(**kwargs)]},
        )

    @classmethod
    def edit_embed(cls, message_id: int, channel_id: int | None = None, **kwargs) -> int:
        """
        Modifie un embed dans un message existant dans un canal Discord.
        :param channel_id: ID du canal.
        :param message_id: ID du message à modifier.
        :param title: Nouveau titre de l'embed (optionnel).
        :param description: Nouvelle description de l'embed (optionnel).
        :param color: Nouvelle couleur de l'embed (en entier, optionnel).
        :return: La réponse de l'API Discord.
        """
        return cls._send_and_get_message_id(
            method=HttpVerb.PATCH,
            channel_id=channel_id,
            endpoint=f"messages/{message_id}",
            json={"embeds": [cls._build_embed(**kwargs)]},
        )
