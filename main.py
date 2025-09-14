import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
import handlers
import menu_builder as mb
from config import Config

logging.basicConfig(level=logging.INFO)

config = Config()

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
router = Router()

mb._handlers_module = handlers
mb._menu_structure = {
    "main": {
        "text": "@welcome",
        "buttons": [
            {"text": "Пункт 1", "action": "goto", "data": "m1"},
            {"text": "Пункт 2", "action": "goto", "data": "m2"},
            {"text": "Пустой пункт", "action": "nothing"},
            {"text": "Показать статистику", "action": "func", "data": "show_stats"},
        ]
    },
    "m1": {
        "text": "Меню 1",
        "buttons": [
            {"text": "Достать из БД", "action": "func", "data": "get_from_db"},
            {"action": "gen", "data": "get_vars", "pattern": {"text": "$text", "action":"func", "data":"$funname"}},
            {"text": "Назад", "action": "goto", "data": "main"}
        ]
    },
    "m2": {
        "text": "Меню 2",
        "buttons": [
            {"action": "gen_manual", "data": "get_my_items"},
            {"text": "Назад", "action": "goto", "data": "main"}
        ]
    }
}
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
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    msg_text, keyboard = mb.build_message(message, "main")
    await message.answer(msg_text, reply_markup=keyboard)

@router.message(Command("test"))
async def cmd_test(message: types.Message):
    await message.answer('test!')

@router.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    await mb.handle_callback(callback)

# ===== Запуск бота =====
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())