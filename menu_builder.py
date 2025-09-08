
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from string import Template


_handlers_module = None
_menu_structure = None
_text_translations = None
_split_symbol = ":"
_translation_symbol_prefix = '@'

class Scope:
    def __init__(self, vars_dict, parent_scope=None):
        self.parent_scope = parent_scope
        self.vars_dict = vars_dict

    def __getitem__(self, key):
        if key in self.vars_dict:
            return self.vars_dict[key]
        if self.parent_scope is not None:
            return self.parent_scope[key]
        return None

# ===== Генерация клавиатуры =====
def build_keyboard(message: types.Message, menu_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for item in _menu_structure[menu_key]["buttons"]:
        add_item_to_keyboard(kb, item, message)
    return kb

def add_item_to_keyboard(kb: InlineKeyboardMarkup, item, message: types.Message):
    if ("action" not in item) and ("text" in item):
        kb.add(InlineKeyboardButton(text=item["text"], callback_data="empty"))
        return
    match item["action"]:
        case "goto" | "func":
            kb.add(InlineKeyboardButton(
                text=item["text"], callback_data=item["action"] + _split_symbol + item["data"]
            ))
        case "gen":
            func = getattr(_handlers_module, item["data"], None)
            user_id = message.chat.id
            items = func(user_id)
            for new_item in items:
                add_item_to_keyboard(kb, new_item, user_id)


def substitute_vars(text: str, scope) -> str:
    return Template(text).safe_substitute(scope)

def load_scope(item, scope=None):
    if 'getter' in item:
        func = getattr(_handlers_module, item["getter"], None)
        vars_dict = func()
        return Scope(vars_dict, scope)
    return None

def get_translation(key: str):
    return _text_translations.get(key[1:], key)

def translate_text(text: str, scope):
    if text[0] == _translation_symbol_prefix:
        text = get_translation(text)
    return substitute_vars(text, scope)

def build_message(msg: types.Message, menu_key: str):
    return _menu_structure[menu_key]["text"], build_keyboard(msg, menu_key)

# ===== Переходы по меню =====

async def handle_callback(callback: types.CallbackQuery):
    action, data = callback.data.split(_split_symbol, 1)

    match action:
        case "goto":
            msg_text, keyboard = build_message(callback.message.chat.id, data)
            await callback.message.edit_text(msg_text, reply_markup=keyboard)
        case "func":
            func = getattr(_handlers_module, data, None)
            if func and callable(func):
                await func(callback)
            else:
                await callback.message.answer(f"⚠ Нет такого действия: {action} {data}")
    await callback.answer()

