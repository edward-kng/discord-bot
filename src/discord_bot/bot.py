from typing import Optional
import discord

from discord_bot.logic.chat import answer
from discord_bot.utils.discord import get_guild, get_channel


class Bot(discord.Client):
    _instance: Optional["Bot"] = None

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    @classmethod
    def get_instance(cls) -> "Bot":
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    async def on_ready(self) -> None:
        if self.user:
            print(self.user.name + " connected!")

        await self.tree.sync()

    def mention(self) -> str:
        return "<@" + str(self.user.id if self.user else "") + ">"

    async def on_message(self, message: discord.Message) -> None:
        if self.user:
            mention = self.mention()

            if mention in message.content or (
                message.reference
                and message.reference.message_id
                and (
                    await message.channel.fetch_message(message.reference.message_id)
                ).author.id
                == self.user.id
            ):
                channel = get_channel(message)
                guild = get_guild(message)
                await message.reply(
                    await answer(
                        self,
                        channel,
                        message.author,
                        guild,
                    )
                )
