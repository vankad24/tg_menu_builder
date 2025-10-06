from dataclasses import dataclass
from typing import Callable

from aiogram.types import InlineKeyboardMarkup


@dataclass
class MessageModel:
    text: str
    keyboard: InlineKeyboardMarkup
    attachment: dict | list[dict] = None
    protect_content: bool = False
    callback_handler: Callable = None

