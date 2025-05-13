from yt_dlp import YoutubeDL

from discord_bot.models.music.song import Song

metadata_client = YoutubeDL()
generic_client = YoutubeDL({"format": "best", "default_search": "ytsearch"})
audio_client = YoutubeDL(
    {"format": "best", "default_search": "ytsearch", "noplaylist": True}
)


def get_youtube_metadata(url: str) -> dict:
    response = metadata_client.extract_info(url, download=False, process=False)

    if not response:
        raise Exception("Error extracting metadata")

    return response


def get_generic_metadata(query: str) -> dict:
    response = generic_client.extract_info(query, download=False)

    if not response:
        raise Exception("Error extracting metadata")

    return response


def get_audio_stream(query: str) -> str:
    response = audio_client.extract_info(query, download=False)

    if not response:
        raise Exception("Error extracting audio stream")

    return response["url"]


def get_audio(song: Song) -> str | None:
    if song.type == "spotify" and song.track_title:
        try:
            metadata = get_generic_metadata(song.query)

        except:
            return None

        # Fallback to search without "audio" if no matching results found
        if (
            len(metadata["entries"]) == 0
            or song.track_title.lower() not in metadata["entries"][0]["title"].lower()
        ):
            try:
                return get_audio_stream(song.query.replace(" audio", ""))
            except:
                return None

        return metadata["entries"][0]["url"]

    return get_audio_stream(song.query)
