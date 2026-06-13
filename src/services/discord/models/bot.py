from discord.ext import commands
from loguru import logger


class DiscordBot(commands.Bot):
    def __init__(self, bot_channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot_channel = bot_channel

    async def setup_hook(self):
        await self.load_extension("apps.discord_app.commands.download")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
