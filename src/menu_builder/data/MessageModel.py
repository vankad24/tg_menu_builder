from dataclasses import dataclass, asdict
from typing import Callable

from aiogram.types import InlineKeyboardMarkup


@dataclass
class MessageModel:
    text: str
    keyboard: InlineKeyboardMarkup
    attachment: dict | list[dict] = None
    protect_content: bool = False
    response_handler: Callable= None

    def as_params(self):
        d = asdict(self)
        keys_to_remove = ['response_handler']
        for key in keys_to_remove:
            d.pop(key, None)
        return d