from aiogram import types
import logging

from src.menu_builder.data.MessageModel import MessageModel


async def get_from_db(message: types.Message):
    # Здесь можно подключаться к БД
    await message.answer("📦 Данные из базы: ...")

async def show_stats(message: types.Message):
    await message.answer("📊 Какая-то статистика")

async def send_message(message: types.Message, text):
    await message.answer(text)


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


async def hello1(message: types.Message):
    await message.answer("hi1")

async def hello2(message: types.Message):
    await message.answer("hi2")

async def input_pressed(message: types.Message):
    await message.answer(f"Введите сообщение:")

async def handle_input(message: types.Message):
    await message.answer(f"Ты ввёл сообщение \"{message.text}\"")

async def func_with_args(message: types.Message, *args):
    await message.answer(f"Переданные аргументы: {args}")

async def func_with_args2(message: types.Message, id, text, num):
    await message.answer(f"Переданные аргументы: {id=} {text=} {num=}")

async def handle_response(response: types.Message, message: types.Message, message_model: MessageModel):
    logging.info(f'handling response {message.chat.id=}!')
    if response.photo:
        logging.info(f'photo={response.photo[-1].file_id}')
    if response.animation:
        logging.info(f'video={response.animation.file_id}')
