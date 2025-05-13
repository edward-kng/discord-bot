import discord

from asyncio import create_task, sleep
from discord_bot.models.music.music_session import MusicSession

sessions: dict[discord.Guild, MusicSession] = {}


async def play_song(
    bot,
    query: str | discord.Attachment,
    pos: int | None,
    user: discord.Member,
    guild: discord.Guild,
    channel: discord.TextChannel,
    shuffle=False,
    play_next=False,
) -> str:
    user_voice = user.voice

    if not user_voice:
        return "Join a voice channel first!"

    voice_channel = user_voice.channel

    if not voice_channel:
        raise Exception("No voice channel found")

    msg = query

    if guild not in sessions:
        await voice_channel.connect()
        voice: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
        sessions[guild] = MusicSession(channel, voice)

        create_task(start_idle_timer(guild))

    create_task(
        sessions[guild].add_song(
            query=query, pos=pos, shuffle=shuffle, play_next=play_next
        )
    )

    return str(msg)


async def skip_song(guild: discord.Guild) -> str:
    if guild in sessions:
        sessions[guild].skip()

        return "Skipped!"
    else:
        return "Not in a voice channel!"


async def end_session(guild: discord.Guild) -> str:
    if guild in sessions:
        session = sessions[guild]
        await session.end()
        sessions.pop(guild)
        msg = "Bye!"
    else:
        msg = "Not in a voice channel!"

    return msg


def pause_song(guild: discord.Guild) -> str:
    if guild in sessions:
        sessions[guild].pause_or_resume()

        return "Paused!"

    return "Not in a voice channel!"


def resume_song(guild: discord.Guild) -> str:
    if guild in sessions:
        sessions[guild].pause_or_resume()

        return "Resumed!"

    return "Not in a voice channel!"


def get_song_queue(guild: discord.Guild) -> str:
    if guild in sessions:
        song_queue = sessions[guild].play_queue

        if len(song_queue) > 10:
            msg = "Next 10 song in queue:"

            for i in range(10):
                msg += "\n" + str(i + 1) + ". " + song_queue[i].title
        else:
            msg = "Queue:"

            for i in range(len(song_queue)):
                msg += "\n" + str(i + 1) + ". " + song_queue[i].title

        return msg
    return "No songs queued!"


def get_current_song(guild: discord.Guild) -> str:
    if guild in sessions:
        session = sessions[guild]
        song = session.now_playing

        if song:
            return "Now playing: " + song.title

    return "No song playing!"


async def start_idle_timer(guild: discord.Guild) -> None:
    session = sessions[guild]

    while session.active:
        idle_secs = 0
        await sleep(0.1)

        while not session.voice.is_playing() and session.active:
            await sleep(1)
            idle_secs += 1

            if idle_secs >= 300:
                await end_session(guild)
                await session.channel.send("I have been idle for too long. Bye!")
                sessions.pop(guild)
