import discord

from discord_bot.models.music.song import Song
from discord_bot.utils.spotify import get_spotify_metadata
from discord_bot.utils.youtube import get_generic_metadata, get_youtube_metadata


def get_songs_from_query(query: str | discord.Attachment) -> list[Song] | None:
    if isinstance(query, discord.Attachment):
        return [Song(query.filename, query.url, query.filename, "file")]

    if "youtube.com" in query:
        track_list = []

        try:
            metadata = get_youtube_metadata(query)
        except:
            return None

        if "entries" in metadata:
            for entry in metadata["entries"]:
                track_list.append(
                    Song(entry["url"], None, entry["title"], "youtube_generic")
                )
        else:
            track_list.append(Song(query, None, metadata["title"], "youtube_generic"))

        return track_list
    elif "spotify.com" in query:
        return get_spotify_metadata(query)
    else:
        try:
            metadata = get_generic_metadata(query)
        except:
            return None

        if "entries" in metadata:
            metadata = metadata["entries"][0]

        return [Song(query, metadata["url"], metadata["title"], "youtube_generic")]
