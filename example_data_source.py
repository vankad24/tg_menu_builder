from datetime import datetime

from src.menu_builder.datasource.AbstractDataSource import AbstractDataSource as ADS

import handlers

_menu_structure = {
    "main": {
        "text": "@welcome",
        "buttons": [
            [
                {"text": "Пункт 1", "action": "goto", "data": "m1"},
                {"text": "Пункт 2", "action": "goto", "data": "m2"}
            ],
            {"text": "Пустой пункт", "action": "nothing"},
            {"text": "Показать статистику", "action": "func", "data": "show_stats"},
            {"text": "Функция с аргументами", "action": "func", "data": "func_with_args", "args": [1, "$USER_ID", "hi", 3]},
            {"text": "Админская кнопка", "action": "goto", "data": "admins_menu", "access": "admin"},
        ]
    },
    "m1": {
        "text": "Меню 1",
        "buttons": [
            [
                {"text": "Достать из БД", "action": "func", "data": "get_from_db"},
                {"action": "gen", "data": "get_vars", "pattern": {"text": "$text", "action":"func", "data":"$funname"}},
            ],
            {"text": "Ввести данные", "action": "input", "data": "input_pressed", "callback": "handle_input"},
            {"text": "Назад", "action": "goto", "data": "main"}
        ]
    },
    "m2": {
        "text": "Меню 2",
        "buttons": [
            {"action": "gen_manual", "data": "get_my_items"},
            {"text": "Назад", "action": "goto", "data": "main"}
        ]
    },
    "admins_menu": {
        "access": "admin",
        "text": "Добро пожаловать в админку. Твой id: $USER_ID",
        "buttons": [
            {"text": "Функция с аргументами", "action": "func", "data": "func_with_args2", "args": ["$USER_ID", "hello, there!", 24]},
            {"text": "Назад", "action": "goto", "data": "main"}
        ]
    }
}

class FuncSource(ADS):
    def get(self, key: str, default=None):
        return getattr(handlers, key, default)


class TranslationSource(ADS):
    def __init__(self):
        self._text_translations = {
            "welcome": "Добро пожаловать, $USER_NAME! Это бот-конструктор"
        }

    def get(self, key: str, default=None):
        return self._text_translations.get(key,default)


class ReservedVarsSource(ADS):
    def __init__(self):
        self._reserved_vars = {
            'USER_ID': lambda msg: msg.chat.id,
            'USER_NAME': lambda msg: 'Vanka',
            'MENU_PREVIOUS_STAGE': lambda msg: 'todo',
            'MENU_CURRENT_STAGE': lambda msg: 'todo',
            'SYS_DATE': lambda msg: datetime.now().strftime("%d.%m.%Y"),
            'SYS_TIME': lambda msg: datetime.now().strftime("%H:%M:%S"),
            'SYS_BOT_NAME': lambda msg: 'Menu builder bot',
        }


    def get(self, key: str, default=None):
        return self._reserved_vars.get(key, default)


class AccessLevelsSource(ADS):
    def __init__(self, admins):
        self._access_levels = {
            "admin": {
                "ids": admins,
                "fail_message": "Вы не админ"
            }
        }

    def get(self, key: str, default=None):
        return self._access_levels.get(key, default)



class MenuStructureSource(ADS):
    def get(self, key: str, default=None):
        return _menu_structure.get(key, default)
