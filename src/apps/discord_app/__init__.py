from discord import Intents

from config import app_settings
from services.discord import NMDownloader

intents = Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

client = NMDownloader(
    intents=intents,
    bot_channel=app_settings.discord.default_channel_id,
    command_prefix=app_settings.discord.command_prefix,
)

if not (token := app_settings.discord.token):
    raise AttributeError("DISCORD_TOKEN not set")

client.run(token=token)
