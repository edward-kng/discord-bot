from asyncio import Condition, Task, create_task, gather, sleep, to_thread
from collections import deque
import random
from typing import Optional

import discord

from discord_bot.models.music.song import Song
from discord_bot.utils.music import get_songs_from_query
from discord_bot.utils.youtube import get_audio


class MusicSession:
    def __init__(
        self, channel: discord.TextChannel, voice: discord.VoiceClient
    ) -> None:
        self.channel = channel
        self.voice = voice
        self.active = True
        self.now_playing: Optional[Song] = None
        self.play_queue: deque[Song] = deque()
        self._download_queue: deque[Song] = deque()
        self._paused = False
        self._skipped = False
        self._download_ready: Condition = Condition()
        self._playback_ready: Condition = Condition()
        self._download_task: Task = create_task(self._start_download())
        self._playback_task: Task = create_task(self._start_playback())

    async def _start_download(self) -> None:
        while self.active:
            if len(self._download_queue) == 0:
                async with self._download_ready:
                    await self._download_ready.wait()

            if not self.active:
                break

            song = self._download_queue[0]

            if not song.audio:
                song.audio = await to_thread(get_audio, song)

            if song == self.play_queue[0]:
                async with self._playback_ready:
                    self._playback_ready.notify()

            self._download_queue.popleft()

    async def _start_playback(self) -> None:
        while self.active:
            if len(self.play_queue) == 0 or not self.play_queue[0].audio:
                async with self._playback_ready:
                    await self._playback_ready.wait()

            if not self.active:
                break

            song = self.play_queue.popleft()

            if not song.audio:
                await self.channel.send("Error: could not find song or invalid URL.")

                continue

            self.voice.play(
                discord.FFmpegPCMAudio(
                    song.audio,
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    options="-vn",
                )
            )

            await self.channel.send(f"Now playing: {song.title}.")
            self.now_playing = song

            while self.active and (self.voice.is_playing() or self._paused):
                await sleep(0.1)

                if self._skipped:
                    self.voice.stop()
                    self._skipped = False

                    break

            self.now_playing = None

            await sleep(1)

    async def add_song(
        self,
        query: str | discord.Attachment,
        shuffle=False,
        pos=None,
        play_next=False,
    ) -> None:
        songs = await to_thread(get_songs_from_query, query)

        if songs is None:
            await self.channel.send("Error: could not find song or invalid URL.")

            return

        songs = songs[pos:]

        if shuffle:
            random.shuffle(songs)

        if not pos:
            pos = 0

        if play_next:
            self._download_queue.extendleft(songs)
            self.play_queue.extendleft(songs)
        else:
            self._download_queue.extend(songs)
            self.play_queue.extend(songs)

        async with self._download_ready:
            self._download_ready.notify()

        msg = "Added to queue: "

        for i in range(min(3, len(songs))):
            msg += "\n" + songs[i].title

        if len(songs) > 3:
            msg += "\n..."

        await self.channel.send(msg)

    async def end(self) -> None:
        if self.voice.is_playing():
            self.voice.stop()

        await self.voice.disconnect()
        self.active = False

        async with self._download_ready:
            self._download_ready.notify_all()

        async with self._playback_ready:
            self._playback_ready.notify_all()

        await gather(self._download_task, self._playback_task)

    def skip(self) -> None:
        self._skipped = True
        self._paused = False

    def pause_or_resume(self) -> None:
        self._paused = not self._paused

        if self._paused:
            self.voice.pause()
        else:
            self.voice.resume()
