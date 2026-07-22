from discord import Intents

from nmdownloader.config import app_settings
from nmdownloader.services.discord import DiscordBot

intents = Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

client = DiscordBot(
    intents=intents,
    bot_channel=app_settings.discord.default_channel_id,
    command_prefix=app_settings.discord.command_prefix,
)
