
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from string import Template


_handlers_module = {}
_menu_structure = {}
_text_translations = {}
_reserved_vars = {}
_split_symbol = ":"
_args_separator = ";"
_translation_symbol_prefix = '@'

class Scope:
    def __init__(self, vars_dict, parent_scope=None, message=None):
        self.parent_scope = parent_scope
        self.vars_dict = vars_dict
        self.message = message

    def __getitem__(self, key):
        if key in self.vars_dict:
            return self.vars_dict[key]
        if self.parent_scope is not None:
            return self.parent_scope[key]
        if key in _reserved_vars and self.message is not None:
            return _reserved_vars[key](self.message)
        return None

# ===== Генерация клавиатуры =====
def build_keyboard(message: types.Message, menu_key: str, scope) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for item in _menu_structure[menu_key]["buttons"]:
        add_item_to_keyboard(kb, item, message, scope)
    return kb

def add_item_to_keyboard(kb: InlineKeyboardMarkup, item, message: types.Message, parent_scope):
    scope = load_scope(item, parent_scope)

    match item["action"]:
        case "goto":
            kb.add(InlineKeyboardButton(
                text=process_text(item, scope), callback_data=substitute_vars(item["action"],scope) + _split_symbol + substitute_vars(item["data"],scope)
            ))
        case "func":
            # todo args
            kb.add(InlineKeyboardButton(
                text=process_text(item, scope), callback_data=substitute_vars(item["action"],scope) + _split_symbol + substitute_vars(item["data"],scope)
            ))
        case "gen":
            func = getattr(_handlers_module, substitute_vars(item["data"], scope), None)
            var_dicts = func()
            pattern_item = item["pattern"]
            for var_dict in var_dicts:
                add_item_to_keyboard(kb,pattern_item,message,Scope(var_dict, scope))
        case "gen_manual":
            func = getattr(_handlers_module, substitute_vars(item["data"],scope), None)
            items = func(message)
            for new_item in items:
                add_item_to_keyboard(kb, new_item, message, scope)
        case "nothing":
            kb.add(InlineKeyboardButton(text=process_text(item, scope), callback_data='nothing'))
        case _:
            raise Exception(f"Нет такого действия: {item['action']}")

def substitute_vars(text: str, scope) -> str:
    return Template(text).safe_substitute(scope)

def load_scope(item, scope=None, message=None):
    if 'getter' in item:
        func = getattr(_handlers_module, item["getter"], None)
        vars_dict = func()
        return Scope(vars_dict, scope, message)
    return Scope({}, scope, message)

def get_translation(key: str):
    return _text_translations.get(key[1:], key)

def process_text(item, scope):
    if 'text' not in item:
        return ''
    text = item['text']
    if text[0] == _translation_symbol_prefix:
        text = get_translation(text)
    return substitute_vars(text, scope)

def build_message(msg: types.Message, menu_key: str):
    stage_scope = load_scope(_menu_structure[menu_key], message=msg)
    # stage_scope.parent_scope = None
    return process_text(_menu_structure[menu_key],stage_scope), build_keyboard(msg, menu_key, stage_scope)

# ===== Переходы по меню =====

async def handle_callback(callback: types.CallbackQuery):
    arr = callback.data.split(_split_symbol, 1)
    if len(arr)==2:
        action = arr[0]
        data = arr[1]
    else:
        action = arr[0]
        data = None

    match action:
        case "goto":
            msg_text, keyboard = build_message(callback.message, data)
            await callback.message.edit_text(msg_text, reply_markup=keyboard)
        case "func":
            func = getattr(_handlers_module, data, None)
            if func and callable(func):
                await func(callback)
        case "nothing":
            ...
        case _:
            await callback.message.answer(f"⚠ Нет такого действия: {action} {data}")
    await callback.answer()

