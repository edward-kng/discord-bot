from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class Song:
    query: str
    audio: Optional[str]
    title: str
    type: Literal["youtube_generic", "spotify", "file"]
    track_title: Optional[str] = None
