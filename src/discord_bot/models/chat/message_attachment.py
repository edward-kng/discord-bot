from dataclasses import dataclass


@dataclass
class MessageAttachment:
    file_name: str
    url: str
