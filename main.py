import asyncio
import logging
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

# ===== Стартовое меню =====
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    msg_text, keyboard = mb.build_message(message, "main")
    await message.answer(msg_text, reply_markup=keyboard)

@dp.callback_query_handler()
async def handle_callback(callback: types.CallbackQuery):
    await mb.handle_callback(callback)

# ===== Запуск бота =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())