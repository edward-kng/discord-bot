from dataclasses import asdict
from datetime import datetime
from typing import Any, Optional

import discord

from discord_bot.models.chat.message_attachment import MessageAttachment
from discord_bot.models.chat.message_sender import MessageSender


class ChatMessage:
    def __init__(
        self,
        sender: MessageSender,
        content: str,
        sent_at: datetime,
        edited_at: Optional[datetime] = None,
        files: Optional[list[MessageAttachment]] = None,
    ):
        self.sender = sender
        self.content = content
        self.sent_at = sent_at
        self.edited_at = edited_at
        self.files = files if files is not None else []

    def to_json(self) -> dict[str, Any]:
        obj = {
            "sender": asdict(self.sender),
            "content": self.content,
            "sent_at": self.sent_at.isoformat(),
        }

        if self.edited_at:
            obj["edited_at"] = self.edited_at.isoformat()

        if self.files:
            obj["files"] = [asdict(file) for file in self.files]

        return obj

    @classmethod
    def from_discord_message(cls, message: discord.Message) -> "ChatMessage":
        data = ChatMessage(
            sender=MessageSender(id=message.author.id, name=message.author.name),
            content=message.content,
            sent_at=message.created_at,
        )

        if message.edited_at:
            data.edited_at = message.edited_at

        if len(message.attachments) > 0:
            data.files = []

            for attachment in message.attachments:
                data.files.append(
                    MessageAttachment(file_name=attachment.filename, url=attachment.url)
                )

        return data
