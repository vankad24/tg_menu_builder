import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import handlers
from menu import MENU_STRUCTURE

logging.basicConfig(level=logging.INFO)


TOKEN = ""
SPLIT_SYMBOL = ":"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ===== Генерация клавиатуры =====
def build_keyboard(user_id, menu_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for item in MENU_STRUCTURE[menu_key]["buttons"]:
        add_item_to_keyboard(kb, item, user_id)
    return kb

def add_item_to_keyboard(kb: InlineKeyboardMarkup, item, user_id):
    if ("action" not in item) and ("text" in item):
        kb.add(InlineKeyboardButton(text=item["text"], callback_data="empty"))
        return
    match item["action"]:
        case "goto" | "func":
            kb.add(InlineKeyboardButton(
                text=item["text"], callback_data=item["action"] + SPLIT_SYMBOL + item["data"]
            ))
        case "additems":
            func = getattr(handlers, item["data"], None)
            items = func(user_id)
            for new_item in items:
                add_item_to_keyboard(kb, new_item, user_id)



def build_message(user_id, menu_key: str):
    return MENU_STRUCTURE[menu_key]["text"], build_keyboard(user_id, menu_key)

# ===== Переходы по меню =====
@dp.callback_query_handler()
async def handle_callback(callback: types.CallbackQuery):
    action, data = callback.data.split(SPLIT_SYMBOL, 1)

    match action:
        case "goto":
            msg_text, keyboard = build_message(callback.message.chat.id, data)
            await callback.message.edit_text(msg_text, reply_markup=keyboard)
        case "func":
            func = getattr(handlers, data, None)
            if func and callable(func):
                await func(callback)
            else:
                await callback.message.answer(f"⚠ Нет такого действия: {action} {data}")
    await callback.answer()

# ===== Стартовое меню =====
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    msg_text, keyboard = build_message(message.chat.id, "main")
    await message.answer(msg_text, reply_markup=keyboard)


# ===== Запуск бота =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())