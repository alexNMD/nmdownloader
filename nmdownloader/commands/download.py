from discord.ext import commands

from loguru import logger

from nmdownloader.config.base import app_settings
from nmdownloader.tasks.download import download_task


class Download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.message.webhook_id:
            return True

        if not (admins := app_settings.discord.admins):
            logger.warning("DISCORD_ADMINS not set. Too broad authorization")
            return True

        # Check admin
        if ctx.author.id not in admins:
            _error_message = "You are not allowed to use this command"
            await ctx.message.reply(_error_message)
            raise commands.CheckFailure(_error_message)

        return True

    @commands.command(name="download", aliases=["d"])
    async def handle_download(self, ctx):
        """USAGE: send link to download file (separate w/ ',')"""

        message = ctx.message
        message_content = message.content.split()
        links, type_dl = str(), None

        match len(message_content):
            case 2:
                _, links = message_content
            case 3:
                _, type_dl, links = message_content
            case _:
                await message.reply(
                    "USAGE: send link to download file (separate w/ ',')"
                )
                return

        try:
            for url in links.split(","):
                task = download_task.delay(
                    url=url,
                    message_id=message.id,
                    channel_id=message.channel.id,
                    type_dl=type_dl,
                )
                logger.info(f"Task sent: {task.id}")
        except Exception as download_error:
            logger.error(f"download failed. Error: {download_error}")
            await message.reply(f"download failed. Error: {download_error}")
        return

    # Cause: Discords Cog command isn't triggered when message is posted from webhook...
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.webhook_id:
            ctx = await self.bot.get_context(message)
            await self.bot.invoke(ctx)


async def setup(bot):
    await bot.add_cog(Download(bot))
