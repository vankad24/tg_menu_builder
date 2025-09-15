
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
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
def build_keyboard(message: Message, menu_key: str, scope) -> InlineKeyboardMarkup:
    buttons_list = process_source(_menu_structure[menu_key]["buttons"], message, scope)
    buttons_list = [x if isinstance(x, list) else [x] for x in buttons_list]
    return InlineKeyboardMarkup(inline_keyboard=buttons_list)

def process_source(source, message: Message, scope):
    buttons_list = []
    for item in source:
        if isinstance(item, list):
            buttons_list.append(process_source(item, message, scope))
        else:
            processed = process_item(item, message, scope)
            if isinstance(processed, list):
                buttons_list.extend(processed)
            else:
                buttons_list.append(processed)
    return buttons_list

def process_item(item, message: Message, parent_scope):
    scope = load_scope(item, parent_scope)

    match item["action"]:
        case "goto":
            return InlineKeyboardButton(
                text=process_text(item, scope),
                callback_data=f"{substitute_vars(item['action'], scope)}{_split_symbol}{substitute_vars(item['data'], scope)}"
            )
        case "func":
            # todo args
            return InlineKeyboardButton(
                text=process_text(item, scope),
                callback_data=f"{substitute_vars(item['action'], scope)}{_split_symbol}{substitute_vars(item['data'], scope)}"
            )
        case "gen":
            func = getattr(_handlers_module, substitute_vars(item["data"], scope), None)
            var_dicts = func()
            pattern_item = item["pattern"]

            buttons = []
            for var_dict in var_dicts:
                buttons.extend(process_source([pattern_item], message, Scope(var_dict, scope)))
            return buttons

        case "gen_manual":
            func = getattr(_handlers_module, substitute_vars(item["data"], scope), None)
            items = func(message)

            return process_source(items, message, scope)

        case "nothing":
            return InlineKeyboardButton(text=process_text(item, scope), callback_data='nothing')
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

