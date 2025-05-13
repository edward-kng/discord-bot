from time import sleep
from discord_bot.bot import Bot
import discord_bot.commands
from discord_bot.config import DISCORD_BOT_TOKEN


def main() -> None:
    if not DISCORD_BOT_TOKEN:
        raise Exception("DISCORD_BOT_TOKEN not provided.")

    sleep(10)
    Bot.get_instance().run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
