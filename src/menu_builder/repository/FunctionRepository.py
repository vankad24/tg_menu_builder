import inspect
import json

from aiogram import types
from .BaseRepository import BaseRepository

class FunctionRepository(BaseRepository):
    def get_functon(self, key: str, default=None):
        return self._data_source.get(key, default)

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
