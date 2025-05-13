from asyncio import Task, create_task, gather, to_thread
import json
import os
import shutil

import discord
from openai import OpenAI
from openai.types.chat.completion_create_params import (
    Function,
)
from discord_bot.config import CHAT_MODEL, OPENAI_API_KEY
from discord_bot.logic.music import (
    play_song,
    get_current_song,
    get_song_queue,
    end_session,
    pause_song,
    resume_song,
    skip_song,
)
from discord_bot.models.chat.chat_message import ChatMessage
from discord_bot.utils.chat import (
    download_attachment,
    get_chat_thread,
)

TMP_DIR = "tmp/"

functions: list[Function] = [
    {
        "name": "send_direct_message",
        "description": "Send a direct message to a user",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user, usually found after an @ symbol",
                },
                "message": {"type": "string", "description": "Message to send"},
            },
            "required": ["user_id", "message"],
        },
    },
    {
        "name": "export_chat_history",
        "description": "Export the chat history to a zip file",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "generate_image",
        "description": "Generate an image from a text prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Prompt to generate image from",
                }
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "play_song",
        "description": "Play a song or add it to the queue",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Song URL or search query",
                },
                "shuffle": {
                    "type": "boolean",
                    "description": "Whether to shuffle the requested playlist of songs. Has no effect on single songs. Defaults to false.",
                },
                "play_next": {
                    "type": "boolean",
                    "description": "Whether to play this song next, putting it in the front of the song queue. Defaults to false.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "skip_song",
        "description": "Skip the current song",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_current_song",
        "description": "Get the name and artist of the current song playing",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "pause_song",
        "description": "Pause the current song",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "resume_song",
        "description": "Resume the current song",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_song_queue",
        "description": "The the current queue of songs to play",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "leave",
        "description": "Leave the voice chat and stop all playing music",
        "parameters": {"type": "object", "properties": {}},
    },
]


if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None


async def create_completion(
    bot,
    chat_history: list[ChatMessage],
    user: discord.User | discord.Member,
    guild: discord.Guild,
    channel: discord.TextChannel,
) -> str:
    if not openai_client:
        raise Exception("OpenAI client not initialised")

    prompt = f"You are a smart chat bot in Discord. You will answer any questions and perform requested actions such as playing music and sending messages. Your name is {bot.user.name}. Previous messages in the chat history may be indicated with the name of the sender in parentheses. Do not include your own name in this manner in your response."

    messages = [
        {
            "role": "system",
            "content": prompt,
        }
    ]

    for message in reversed(chat_history):
        is_bot = message.sender.id == bot.user.id
        content = message.content.replace(str(bot.user.id), bot.user.name)

        if not is_bot:
            content = f"({message.sender.name}) {content}"

        messages.append(
            {
                "role": ("assistant" if is_bot else "user"),
                "content": content,
            }
        )

    data = await to_thread(
        openai_client.chat.completions.create,
        model=CHAT_MODEL,
        messages=messages,  # type: ignore
        functions=functions,
    )
    data = data.choices[0]
    msg = data.message.content
    call = data.message.function_call

    if call:
        args = json.loads(call.arguments)
        function = call.name

        if function == "send_direct_message":
            await dm_user(bot, args["user_id"], args["message"])
            msg = "Okay!"
        elif function == "export_chat_history":
            msg = "Okay! Just a moment."
            create_task(export_history(channel))
        elif function == "generate_image":
            msg = await generate_image(args["prompt"])
        elif function == "play_song":
            if not isinstance(user, discord.Member):
                raise Exception("User is not a member of the guild")

            msg = await play_song(
                bot,
                args["query"],
                0,
                user,
                guild,
                channel,
                shuffle=args["shuffle"] if "shuffle" in args else False,
                play_next=args["play_next"] if "play_next" in args else False,
            )
        elif function == "get_current_song":
            msg = get_current_song(guild)
        elif function == "skip_song":
            msg = await skip_song(guild)
        elif function == "pause_song":
            msg = pause_song(guild)
        elif function == "resume_song":
            msg = resume_song(guild)
        elif function == "get_song_queue":
            msg = get_song_queue(guild)
        else:
            msg = await end_session(guild)

    if not msg:
        raise Exception("Error creating completion")

    return msg


async def answer(
    bot,
    channel: discord.TextChannel,
    user: discord.User | discord.Member,
    guild: discord.Guild,
) -> str:
    if not openai_client:
        return "Chat not enabled!"

    chat_history = await get_chat_thread(bot, channel)

    async with channel.typing():
        return await create_completion(bot, chat_history, user, guild, channel)


async def dm_user(bot: discord.Client, user_id: int, msg: str) -> None:
    user = await bot.fetch_user(user_id)
    await user.send(msg)


async def generate_image(prompt: str) -> str:
    if not openai_client:
        raise Exception("OpenAI client not initialised")

    response = await to_thread(
        openai_client.images.generate,
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    if not response.data or len(response.data) == 0 or not response.data[0].url:
        raise Exception("Error generating image")

    return response.data[0].url


async def export_history(channel: discord.TextChannel) -> None:
    path = TMP_DIR + str(channel.id)

    if not os.path.exists(path + "/files"):
        os.makedirs(path + "/files")

    messages: list[ChatMessage] = []
    download_tasks: list[Task] = []

    async for message in channel.history():
        parsed_message = ChatMessage.from_discord_message(message)
        messages.append(parsed_message)

        if parsed_message.files:
            for file in parsed_message.files:
                url = file.url
                file_name = file.file_name

                download_tasks.append(
                    create_task(to_thread(download_attachment, url, file_name, path))
                )

    await gather(*download_tasks)

    with open(path + "/history.json", "w") as history_file:
        json.dump(
            {"history": list(map(lambda message: message.to_json(), messages))},
            history_file,
        )

    shutil.make_archive(path, "zip", path)
    zip_path = path + ".zip"
    await channel.send("Chat history export finished!", file=discord.File(zip_path))
    shutil.rmtree(path)
    os.remove(zip_path)
