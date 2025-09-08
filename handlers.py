from aiogram import types

async def get_from_db(callback: types.CallbackQuery):
    # Здесь можно подключаться к БД
    await callback.message.answer("📦 Данные из базы: ...")

async def show_stats(callback: types.CallbackQuery):
    await callback.message.answer("📊 Какая-то статистика")

async def send_message(callback: types.CallbackQuery, text):
    await callback.message.answer(text)


def get_my_items(user_id):
    return [
        {"text": "Элемент 1", "action": "func", "data": "get_from_db"},
        {"text": "id "+str(user_id)},
        {"text": "Вернуться в меню", "action": "goto", "data": "main"}
    ]
