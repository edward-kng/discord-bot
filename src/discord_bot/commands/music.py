import typing

import discord
from discord_bot.bot import Bot
from discord_bot.logic.music import (
    play_song,
    get_current_song,
    get_song_queue,
    pause_song,
    resume_song,
    skip_song,
    end_session,
)
from discord_bot.utils.discord import get_guild, get_guild_member, get_channel

bot = Bot.get_instance()


@bot.tree.command()
async def play(
    interaction: discord.Interaction, song: str, pos: typing.Optional[int]
) -> None:
    user = get_guild_member(interaction)
    guild = get_guild(interaction)
    channel = get_channel(interaction)
    await interaction.response.send_message(
        await play_song(bot, song, pos, user, guild, channel)
    )


@bot.tree.command()
async def play_next(
    interaction: discord.Interaction, song: str, pos: typing.Optional[int]
) -> None:
    user = get_guild_member(interaction)
    guild = get_guild(interaction)
    channel = get_channel(interaction)
    await interaction.response.send_message(
        await play_song(
            bot,
            song,
            pos,
            user,
            guild,
            channel,
            play_next=True,
        )
    )


@bot.tree.command()
async def play_file(interaction: discord.Interaction, file: discord.Attachment) -> None:
    user = get_guild_member(interaction)
    guild = get_guild(interaction)
    channel = get_channel(interaction)
    await interaction.response.send_message(
        await play_song(bot, file, 0, user, guild, channel)
    )


@bot.tree.command()
async def play_file_next(
    interaction: discord.Interaction, file: discord.Attachment
) -> None:
    user = get_guild_member(interaction)
    guild = get_guild(interaction)
    channel = get_channel(interaction)
    await interaction.response.send_message(
        await play_song(
            bot,
            file,
            0,
            user,
            guild,
            channel,
            play_next=True,
        )
    )


@bot.tree.command()
async def shuffle(interaction: discord.Interaction, song: str) -> None:
    user = get_guild_member(interaction)
    guild = get_guild(interaction)
    channel = get_channel(interaction)
    await interaction.response.send_message(
        await play_song(
            bot,
            song,
            0,
            user,
            guild,
            channel,
            shuffle=True,
        )
    )


@bot.tree.command()
async def skip(interaction: discord.Interaction) -> None:
    guild = get_guild(interaction)
    await interaction.response.send_message(await skip_song(guild))


@bot.tree.command()
async def leave(interaction: discord.Interaction) -> None:
    guild = get_guild(interaction)
    await interaction.response.send_message(await end_session(guild))


@bot.tree.command()
async def pause(interaction: discord.Interaction) -> None:
    guild = get_guild(interaction)
    await interaction.response.send_message(pause_song(guild))


@bot.tree.command()
async def resume(interaction: discord.Interaction) -> None:
    guild = get_guild(interaction)
    await interaction.response.send_message(resume_song(guild))


@bot.tree.command()
async def queue(interaction: discord.Interaction) -> None:
    guild = get_guild(interaction)
    await interaction.response.send_message(get_song_queue(guild))


@bot.tree.command()
async def now_playing(interaction: discord.Interaction) -> None:
    guild = get_guild(interaction)
    await interaction.response.send_message(get_current_song(guild))
