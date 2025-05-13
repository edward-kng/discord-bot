import discord
import requests

from discord_bot.config import CHAT_CONTEXT_LIMIT
from discord_bot.models.chat.chat_message import ChatMessage


def download_attachment(url: str, file_name: str, path: str) -> None:
    response = requests.get(url)

    with open(str(path) + "/files/" + file_name, "wb") as file:
        file.write(response.content)


async def get_chat_thread(bot, channel: discord.TextChannel) -> list[ChatMessage]:
    messages: list[ChatMessage] = []
    found_start = False
    i = CHAT_CONTEXT_LIMIT

    async for message in channel.history():
        messages.append(ChatMessage.from_discord_message(message))

        if not found_start and bot.mention() in message.content:
            found_start = True
        elif found_start:
            i -= 1

        if found_start and i <= 0:
            break

    return messages
