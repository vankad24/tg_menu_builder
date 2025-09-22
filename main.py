import asyncio
import logging
from example_data_source import *

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from src.menu_builder import menu_builder as mb
from bot_init import config

logging.basicConfig(level=logging.INFO)


bot = Bot(token=config.BOT_TOKEN)
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
    func_source = FuncSource()
    translation_source = TranslationSource()
    reserved_vars_source = ReservedVarsSource()
    access_levels_source = AccessLevelsSource()
    menu_structure_source = MenuStructureSource()


    mb.createRepositoryStorage(
        function_src=func_source,
        translation_src=translation_source,
        reserved_vars_src=reserved_vars_source,
        access_levels_src=access_levels_source,
        menu_structure_src=menu_structure_source
    )


async def main():
    init_menu_builder()
    mb.register_handlers(router)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())