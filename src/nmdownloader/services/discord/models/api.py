from datetime import UTC, datetime
from typing import TypedDict

import requests

from nmdownloader.config import app_settings


class EmbedFieldPayload(TypedDict):
    name: str
    value: str
    inline: bool


class EmbedPayload(TypedDict):
    title: str
    description: str
    color: int
    fields: list[dict[str, str | bool]]
    timestamp: str


class DiscordAPI:
    TIMEOUT = 10
    BASE_URL = app_settings.discord.api_url
    TOKEN = app_settings.discord.token

    @classmethod
    def _send_and_get_message_id(cls, endpoint: str, **kwargs) -> int:
        url = f"{cls.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bot {cls.TOKEN}",
            "Content-Type": "application/json",
        }

        response = requests.request(url=url, headers=headers, timeout=cls.TIMEOUT, **kwargs)
        response.raise_for_status()
        response_json = response.json()

        if not (message_id := response_json.get("id")):
            raise ValueError("Unable to retrieve message id from Discord API")

        return message_id

    @classmethod
    def _build_embed(
        cls, title: str, description: str, color: int, fields: list[dict[str, str]] | None
    ) -> EmbedPayload:
        embed_payload: EmbedPayload = {
            "title": title,
            "description": description,
            "color": color,
            "fields": [],
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if fields:
            embed_payload["fields"] = [
                {"name": field["name"], "value": field["value"], "inline": True} for field in fields
            ]

        return embed_payload

    @classmethod
    def reply_with_embed(cls, channel_id: int, message_id: int, **kwargs) -> int:
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
            method="POST",
            endpoint=f"channels/{channel_id}/messages",
            json={"embeds": [cls._build_embed(**kwargs)], "message_reference": {"message_id": message_id}},
        )

    @classmethod
    def send_embed(cls, channel_id: int, **kwargs) -> int:
        """
        Envoie un message dans un canal Discord avec un embed (sans répondre à un autre message).
        :param channel_id: ID du canal où envoyer le message.
        :param title: Le titre de l'embed.
        :param description: La description de l'embed.
        :param color: La couleur de l'embed (en hexadécimal ou entier).
        :return: La réponse de l'API Discord.
        """
        return cls._send_and_get_message_id(
            method="POST", endpoint=f"channels/{channel_id}/messages", json={"embeds": [cls._build_embed(**kwargs)]}
        )

    @classmethod
    def edit_embed(cls, channel_id: int, message_id: int, **kwargs) -> int:
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
            method="PATCH",
            endpoint=f"channels/{channel_id}/messages/{message_id}",
            json={"embeds": [cls._build_embed(**kwargs)]},
        )
