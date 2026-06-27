from apps.discord_app import client
from config import app_settings


def bot() -> None:
    if not (token := app_settings.discord.token):
        raise AttributeError("DISCORD_TOKEN not set")

    client.run(token=token)


if __name__ == "__main__":
    bot()
