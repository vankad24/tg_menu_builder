import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
import handlers
from menu import MENU_STRUCTURE
import menu_builder as mb

logging.basicConfig(level=logging.INFO)

TOKEN = ""

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

mb._handlers_module = handlers
mb._menu_structure = MENU_STRUCTURE
mb._text_translations = {
    "welcome": "Добро пожаловать, $USER_NAME! Это бот-конструктор"
}
mb._reserved_vars = {
    'USER_ID': lambda msg: msg.chat.id,
    'USER_NAME': lambda msg: 'Vanka',
    'MENU_PREVIOUS_STAGE': lambda msg: 'todo',
    'MENU_CURRENT_STAGE': lambda msg: 'todo',
    'SYS_DATE': lambda msg: datetime.now().strftime("%d.%m.%Y"),
    'SYS_TIME': lambda msg: datetime.now().strftime("%H:%M:%S"),
    'SYS_BOT_NAME': lambda msg: 'Menu builder bot',
}

# ===== Стартовое меню =====
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    msg_text, keyboard = mb.build_message(message, "main")
    await message.answer(msg_text, reply_markup=keyboard)

@dp.message_handler(commands=["test"])
async def cmd_start(message: types.Message):
    await message.answer('test!')

@dp.callback_query_handler()
async def handle_callback(callback: types.CallbackQuery):
    await mb.handle_callback(callback)

# ===== Запуск бота =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())