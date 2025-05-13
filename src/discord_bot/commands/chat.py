import discord
from discord_bot.bot import Bot
from discord_bot.logic.chat import (
    generate_image as generate_image_logic,
    export_history as export_history_logic,
)
from discord_bot.utils.discord import get_channel

bot = Bot.get_instance()


@bot.tree.command()
async def export_history(interaction: discord.Interaction) -> None:
    channel = get_channel(interaction)
    await interaction.response.send_message("Exporting chat history...")
    await export_history_logic(channel)


@bot.tree.command()
async def generate_image(interaction: discord.Interaction, prompt: str) -> None:
    channel = get_channel(interaction)
    await interaction.response.send_message("Generating image: " + prompt)
    await channel.send(await generate_image_logic(prompt))
