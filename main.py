import asyncio
import logging

from Config import Config
from example_data_source import *

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from src.menu_builder import menu_builder as mb

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()
router = Router()

# ===== Стартовое меню =====
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await mb.handle_send_menu(message, "main")

@router.message(Command("test"))
async def cmd_test(message: types.Message):
    await message.answer('test!')

# ===== Запуск бота =====

def init_menu_builder():
    mb.createRepositoryStorage(
        function_src=FuncSource(),
        translation_src=TranslationSource(),
        reserved_vars_src=ReservedVarsSource(),
        access_levels_src=AccessLevelsSource(Config.BOT_ADMINS),
        menu_structure_src=MenuStructureSource()
    )

async def main():
    init_menu_builder()
    mb.register_handlers(router)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())