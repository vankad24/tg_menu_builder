from aiogram.filters.callback_data import CallbackData  # aiogram v3

class MenuCbData(CallbackData, prefix="menu"):
    action: str
    data: str | None = None
    args: str | None = None
    callback: str | None = None
