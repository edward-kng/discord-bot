import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CHAT_CONTEXT_LIMIT = 10
CHAT_MODEL = "gpt-4o-mini"
