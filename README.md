# Discord Bot

An AI Discord bot that can play music from YouTube and Spotify, export your chat history and answer all your questions.

## Usage

To chat, simply send a message and mention the bot (with @). Reply to continue the conversation. The bot will respond to instructions in natural langauge, or you can use any of the slash commands below if you prefer.

## Commands

### Music

- `/play <song URL or title> [track nr to play from]` - play a song/playlist
- `/play_next <song URL or title> [track nr to play from]` - play a song next,
  before every other song in the queue
- `/play_file <file>` - play an audio file
- `/shuffle <playlist URL>` - shuffle and play a playlist
- `/skip` - skip current song
- `/pause` - pause current song
- `/resume` - resume current song
- `/queue` - show song queue
- `/leave` - leave voice chat
- `/now_playing` - show current song

### Chat

- `/export_history` - export entire chat history to a JSON file
- `/generate_mage <prompt>` - generate an image

## Setup

### Prerequisites

- Python
- Poetry
  <br>
  <br>

1. Install dependencies:

   ```
   poetry install
   ```

2. Create an application and bot on the
   [Discord Developer](https://discord.com/developers) site and add it to your
   server.
3. Copy your bot's token and create the `DISCORD_BOT_TOKEN` environment variable in your shell config or
   create a `.env` file containing:

   ```
   DISCORD_BOT_TOKEN=<your token>
   ```

4. Run the bot with:

   ```
   python src/discord_bot/run.py
   ```

### Chat Setup

1. Get an OpenAI API key and top up your account at the
   [OpenAI developer platform](https://platform.openai.com/).
2. Create the `OPENAI_API_KEY` environment variable:

   ```
   OPENAI_API_KEY=<your key>
   ```

### Spotify Setup

1. Create an application on the
   [Spotify for Developers](https://developer.spotify.com/) site.
2. Create the following environment variables:

   ```
   SPOTIPY_CLIENT_ID=<your client ID>
   SPOTIPY_CLIENT_SECRET=<your client secret>
   ```

## Notes

For technical and legal reasons, the bot does not download any songs from
Spotify directly. Instead, it grabs each song's metadata using the
Spotify Web API and downloads an equivalent audio file from YouTube.

## Licence

Discord Bot  
Copyright (C) 2025 Edward Kang

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see
[https://www.gnu.org/licenses/](https://www.gnu.org/licenses/).
