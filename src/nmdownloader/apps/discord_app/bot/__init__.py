from discord.ext import commands
from loguru import logger


class DiscordBot(commands.Bot):
    def __init__(self, bot_channel: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot_channel = bot_channel

    async def setup_hook(self) -> None:
        await self.load_extension("..commands.download", package=__name__)

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user}")
