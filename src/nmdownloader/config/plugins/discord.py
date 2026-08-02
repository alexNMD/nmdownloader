from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DiscordConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DISCORD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    token: str | None = None
    admins: list[int] | None = None
    default_channel_id: int = Field(default=0)
    command_prefix: str = "!"
    refresh_rate: int = Field(default=10)
    api_url: str = "https://discord.com/api"
    api_version: str = "v10"
