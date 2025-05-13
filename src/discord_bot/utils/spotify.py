import spotipy

from discord_bot.config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from discord_bot.models.music.song import Song

if SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET:
    spotify_client = spotipy.Spotify(
        client_credentials_manager=spotipy.oauth2.SpotifyClientCredentials(
            client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
        )
    )
else:
    spotify_client = None


def get_song_from_spotify_metadata(track: dict) -> Song:
    song = Song(
        track["artists"][0]["name"],
        None,
        track["artists"][0]["name"],
        "spotify",
        track["name"],
    )

    for i in range(1, len(track["artists"])):
        song.title += ", " + track["artists"][i]["name"]
        song.query += " " + track["artists"][i]["name"]

    song.title += " - " + track["name"]

    # Add "audio" to query to avoid downloading music videos
    song.query += " " + track["name"] + " audio"

    return song


def get_spotify_metadata(query: str) -> list[Song] | None:
    track_list = []

    if spotify_client is None:
        return None

    if "playlist" in query:
        try:
            playlist = spotify_client.playlist_tracks(query)
        except:
            return None

        if not playlist:
            return None

        for track in playlist["items"]:
            track_list.append(get_song_from_spotify_metadata(track["track"]))
    elif "album" in query:
        try:
            album = spotify_client.album_tracks(query)
        except:
            return None

        if not album:
            return None

        for track in album["items"]:
            track_list.append(get_song_from_spotify_metadata(track))
    else:
        try:
            track = spotify_client.track(query)
        except:
            return None

        if not track:
            return None

        track_list.append(get_song_from_spotify_metadata(track))

    return track_list
