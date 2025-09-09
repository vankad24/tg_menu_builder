from aiogram import types

async def get_from_db(callback: types.CallbackQuery):
    # Здесь можно подключаться к БД
    await callback.message.answer("📦 Данные из базы: ...")

async def show_stats(callback: types.CallbackQuery):
    await callback.message.answer("📊 Какая-то статистика")

async def send_message(callback: types.CallbackQuery, text):
    await callback.message.answer(text)


def get_my_items(message):
    return [
        {"text": "Элемент 1", "action": "func", "data": "get_from_db"},
        {"text": "id "+str(message.chat.id), "action":"nothing"},
        {"text": "id2 $USER_ID", "action":"nothing"},
        {"text": "Вернуться в меню", "action": "goto", "data": "main"}
    ]


def get_vars():
    return [
        {"text": "Элемент 1", "funname": "hello1"},
        {"text": "Элемент 2", "funname": "hello2"},
    ]


async def hello1(callback: types.CallbackQuery):
    await callback.message.answer("hi1")

async def hello2(callback: types.CallbackQuery):
    await callback.message.answer("hi2")
