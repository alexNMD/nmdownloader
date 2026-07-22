import requests

from config import app_settings


class DiscordAPI:
    TIMEOUT = 10
    BASE_URL = app_settings.discord.api_url
    TOKEN = app_settings.discord.token

    @classmethod
    def _call(cls, endpoint: str, **kwargs) -> dict:
        url = f"{cls.BASE_URL}/{endpoint}"
        headers = { "Authorization": f"Bot {cls.TOKEN}", "Content-Type": "application/json"}

        response = requests.request(url=url, headers=headers, timeout=cls.TIMEOUT, **kwargs)
        response.raise_for_status()

        return response.json()

    @classmethod
    def reply_with_embed(cls, channel_id, message_id, title, description, color):
        """
        Répond à un message dans un canal Discord avec un embed.
        :param channel_id: ID du canal où le message a été envoyé.
        :param message_id: ID du message auquel répondre.
        :param title: Le titre de l'embed.
        :param description: La description de l'embed.
        :param color: La couleur de l'embed (en hexadécimal).
        :return: La réponse de l'API Discord.
        """
        embed = {
            "title": title,
            "description": description,
            "color": color,
        }
        data = {"embeds": [embed], "message_reference": {"message_id": message_id}}

        response = cls._call(method="POST", endpoint=f"channels/{channel_id}/messages", json=data)

        return response.get("id")

    @classmethod
    def send_embed(cls, channel_id, title, description, color):
        """
        Envoie un message dans un canal Discord avec un embed (sans répondre à un autre message).
        :param channel_id: ID du canal où envoyer le message.
        :param title: Le titre de l'embed.
        :param description: La description de l'embed.
        :param color: La couleur de l'embed (en hexadécimal ou entier).
        :return: La réponse de l'API Discord.
        """
        embed = {
            "title": title,
            "description": description,
            "color": color,
        }
        data = {"embeds": [embed]}

        response = cls._call(method="POST", endpoint=f"channels/{channel_id}/messages", json=data)

        return response.get("id")

    @classmethod
    def edit_embed(
        cls, channel_id, message_id, title=None, description=None, color=None
    ):
        """
        Modifie un embed dans un message existant dans un canal Discord.
        :param channel_id: ID du canal.
        :param message_id: ID du message à modifier.
        :param title: Nouveau titre de l'embed (optionnel).
        :param description: Nouvelle description de l'embed (optionnel).
        :param color: Nouvelle couleur de l'embed (en entier, optionnel).
        :return: La réponse de l'API Discord.
        """
        embed = {}
        if title is not None:
            embed["title"] = title
        if description is not None:
            embed["description"] = description
        if color is not None:
            embed["color"] = color

        data = {"embeds": [embed]}

        response = cls._call(method="PATCH", endpoint=f"channels/{channel_id}/messages/{message_id}", json=data)

        return response

    @classmethod
    def send_message(cls, channel_id, content):
        """
        Envoie un message à un canal Discord spécifié.
        :param channel_id: ID du canal Discord.
        :param content: Le contenu du message.
        :return: La réponse de l'API Discord.
        """
        data = {"content": content}

        response = cls._call(method="POST", endpoint=f"channels/{channel_id}/messages", json=data)

        return response.get("id")

    @classmethod
    def edit_message(cls, channel_id, message_id, new_content):
        """
        Modifie un message existant dans un canal Discord.
        :param channel_id: ID du canal où le message a été envoyé.
        :param message_id: ID du message à modifier.
        :param new_content: Nouveau contenu du message.
        :return: La réponse de l'API Discord.
        """
        data = {"content": new_content}

        response = cls._call(method="PATCH", endpoint=f"channels/{channel_id}/messages/{message_id}", json=data)

        return response

    @classmethod
    def reply_to_message(cls, channel_id, message_id, content):
        """
        Répond à un message dans un canal Discord.
        :param channel_id: ID du canal où le message a été envoyé.
        :param message_id: ID du message auquel répondre.
        :param content: Contenu de la réponse.
        :return: L'ID du message envoyé.
        """
        data = {"content": content, "message_reference": {"message_id": message_id}}

        response = cls._call(method="POST", endpoint=f"channels/{channel_id}/messages", json=data)

        return response.get("id")
