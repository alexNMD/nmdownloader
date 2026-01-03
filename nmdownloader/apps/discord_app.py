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

if __name__ == "__main__":
    client.run(token=app_settings.discord.token, log_level=app_settings.log_level)
