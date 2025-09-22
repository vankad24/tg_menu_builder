import inspect
import json

from aiogram import types
from src.menu_builder.datasource.AbstractDataSource import AbstractDataSource as ADS
from src.menu_builder.repository.BaseRepository import BaseRepository

class FunctionRepository(BaseRepository):
    def __init__(self, callback_handler_src: ADS, getter_src: ADS, gen_items_src: ADS):
        super().__init__(callback_handler_src)
        if not isinstance(callback_handler_src, ADS):
            raise TypeError(f"callback_handler_src должен быть экземпляром {ADS}")
        if not isinstance(getter_src, ADS):
            raise TypeError(f"getter_src должен быть экземпляром {ADS}")
        if not isinstance(gen_items_src, ADS):
            raise TypeError(f"gen_items_src должен быть экземпляром {ADS}")

        self._callback_handler_src = callback_handler_src
        self._getter_src = getter_src
        self._gen_items_src = gen_items_src

    def get_callback_handler(self, key: str):
        return self._callback_handler_src.get(key)

    def get_getter(self, key: str):
        return self._getter_src.get(key)

    def get_gen_items_func(self, key: str):
        return self._gen_items_src.get(key)

def get_func_args(message: types.Message, func, args: str | None = None):

    # Парсим аргументы
    if args:
        try:
            parsed_args = json.loads(args)
        except Exception:
            parsed_args = args
    else:
        parsed_args = None

    # Готовим аргументы для вызова
    if isinstance(parsed_args, dict):
        call_args = (message,)
        call_kwargs = parsed_args
    elif isinstance(parsed_args, list):
        call_args = (message, *parsed_args)
        call_kwargs = {}
    elif parsed_args is not None:
        call_args = (message, parsed_args)
        call_kwargs = {}
    else:
        call_args = (message,)
        call_kwargs = {}

    # Получаем сигнатуру функции
    sig = inspect.signature(func)
    params = sig.parameters

    # Если функция не принимает аргументов — не передаём
    if not params:
        call_args, call_kwargs = (), {}
    return call_args, call_kwargs

async def async_handle_func_call(message: types.Message, func, args: str | None = None):
    if not (func and callable(func)):
        return None
    call_args, call_kwargs = get_func_args(message, func, args)
    return await func(*call_args, **call_kwargs)

def handle_func_call(message: types.Message, func, args: str | None = None):
    if not (func and callable(func)):
        return None
    call_args, call_kwargs = get_func_args(message, func, args)
    return func(*call_args, **call_kwargs)
