import discord

from nmdownloader.config import app_settings
from nmdownloader.services.bot import NMDownloader

custom_intents = discord.Intents.default()
custom_intents.typing = False
custom_intents.presences = False
custom_intents.message_content = True

client = NMDownloader(
    intents=custom_intents,
    bot_channel=app_settings.discord.default_channel_id,
    command_prefix=app_settings.discord.command_prefix,
)

def main():
    if not (token := app_settings.discord.token):
        raise AttributeError("DISCORD_TOKEN not set")

    client.run(token=token)

if __name__ == "__main__":
    main()
