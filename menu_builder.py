
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

_handlers_module = None
_menu_structure = None
_split_symbol = ":"

# ===== Генерация клавиатуры =====
def build_keyboard(user_id, menu_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for item in _menu_structure[menu_key]["buttons"]:
        add_item_to_keyboard(kb, item, user_id)
    return kb

def add_item_to_keyboard(kb: InlineKeyboardMarkup, item, user_id):
    if ("action" not in item) and ("text" in item):
        kb.add(InlineKeyboardButton(text=item["text"], callback_data="empty"))
        return
    match item["action"]:
        case "goto" | "func":
            kb.add(InlineKeyboardButton(
                text=item["text"], callback_data=item["action"] + _split_symbol + item["data"]
            ))
        case "gen":
            func = getattr(_handlers_module, item["data"], None)
            items = func(user_id)
            for new_item in items:
                add_item_to_keyboard(kb, new_item, user_id)


# ===== Переходы по меню =====

async def handle_callback(callback: types.CallbackQuery):
    action, data = callback.data.split(_split_symbol, 1)

    match action:
        case "goto":
            msg_text, keyboard = build_message(callback.message.chat.id, data)
            await callback.message.edit_text(msg_text, reply_markup=keyboard)
        case "func":
            func = getattr(_handlers_module, data, None)
            if func and callable(func):
                await func(callback)
            else:
                await callback.message.answer(f"⚠ Нет такого действия: {action} {data}")
    await callback.answer()

