import json
from string import Template

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from data.RepositoryStorage import RepositoryStorage
from repository.AccessRepository import AccessRepository
from repository.FunctionRepository import FunctionRepository
from repository.MenuRepository import MenuRepository
from repository.ScopeRepository import ScopeRepository
from repository.TranslationRepository import TranslationRepository

_handlers_module = {}
_menu_structure = {}
_text_translations = {}
_reserved_vars = {}
_split_symbol = ":"
_translation_symbol_prefix = '@'
_access_levels = {}

rs: RepositoryStorage = None

def initRepositoryStorage(callback_handler_src, getter_src, gen_items_src, translation_src, reserved_vars_src, access_levels_src, menu_structure_src):
    global rs
    rs = RepositoryStorage(
        funRep=FunctionRepository(callback_handler_src, getter_src, gen_items_src),
        transRep=TranslationRepository(translation_src),
        scopeRep=ScopeRepository(reserved_vars_src),
        accessRep=AccessRepository(access_levels_src),
        menuRep=MenuRepository(menu_structure_src)
    )



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
def build_keyboard(message: Message, menu_item, scope) -> InlineKeyboardMarkup:
    buttons_list = process_source(menu_item["buttons"], message, scope)
    buttons_list = [x if isinstance(x, list) else [x] for x in buttons_list]
    return InlineKeyboardMarkup(inline_keyboard=buttons_list)

def process_source(source, message: Message, scope):
    buttons_list = []
    for item in source:
        if isinstance(item, list):
            buttons_list.append(process_source(item, message, scope))
        else:
            processed = process_item(item, message, scope)
            if processed is not None:
                if isinstance(processed, list):
                    buttons_list.extend(processed)
                else:
                    buttons_list.append(processed)
    return buttons_list

def pack_callback_data(item, scope: Scope, keys:list):
    result = []
    for key in keys:
        result.append(substitute_vars(item[key], scope))
    return _split_symbol.join(result)

def process_item(item, message: Message, parent_scope):
    scope = load_scope(item, parent_scope)
    if "access" in item:
        access_level = item["access"]
        if not has_access(access_level, message):
            return None

    action = substitute_vars(item["action"], scope)
    match action:
        case "goto":
            return InlineKeyboardButton(
                text=process_text(item, scope),
                callback_data=MenuCbData(action="goto", data=substitute_vars(item["data"], scope)).pack()
            )
        case "func":
            args = None
            if "args" in item:
                arr = [
                    substitute_vars(x, scope) if isinstance(x, str) else x
                    for x in item["args"]
                ]
                args = json.dumps(arr)
            return InlineKeyboardButton(
                text=process_text(item, scope),
                callback_data=MenuCbData(
                    action="func",
                    data=substitute_vars(item["data"], scope),
                    args=args
                ).pack()
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
        case "input":
            return InlineKeyboardButton(
                text=process_text(item, scope),
                callback_data=MenuCbData(
                    action="input",
                    data=substitute_vars(item["data"], scope),
                    callback=substitute_vars(item["callback"], scope)
                ).pack()
            )
        case "nothing":
            return InlineKeyboardButton(text=process_text(item, scope), callback_data=MenuCbData(action="nothing").pack())

        case _:
            raise Exception(f"Нет такого действия: {item['action']}")

def substitute_vars(text: str, scope) -> str:
    return Template(text).safe_substitute(scope)

def load_scope(item, parent_scope):
    if 'getter' in item:
        func = getattr(_handlers_module, item["getter"], None)
        vars_dict = func()
        return Scope(vars_dict, parent_scope)
    return parent_scope

def get_translation(key: str):
    return _text_translations.get(key[1:], key)

def process_text(item, scope):
    if 'text' not in item:
        return ''
    text = item['text']
    if text[0] == _translation_symbol_prefix:
        text = get_translation(text)
    return substitute_vars(text, scope)



def has_access(access_level, msg: types.Message):
    if access_level not in _access_levels:
        return False
    return msg.chat.id in _access_levels[access_level]['ids']

def build_message(message: types.Message, menu_item):
    stage_scope = load_scope(menu_item, Scope({}, message=message))
    return process_text(menu_item, stage_scope), build_keyboard(message, menu_item, stage_scope)

async def handle_send_menu(message: types.Message, menu_key: str, edit_message=False):
    menu_item = _menu_structure[menu_key]

    #check access level
    if "access" in menu_item:
        access_level = menu_item["access"]
        if not has_access(access_level, message):
            fail_message = _access_levels[access_level].get('fail_message', '')
            if fail_message:
                await message.answer(fail_message)
            return

    msg_text, keyboard = build_message(message, menu_item)
    if msg_text:
        if edit_message:
            await message.edit_text(msg_text, reply_markup=keyboard)
        else:
            await message.answer(msg_text, reply_markup=keyboard)

async def handle_func_call(message: Message, fun_name: str, args: str | None = None):
    func = getattr(_handlers_module, fun_name, None)
    if func and callable(func):
        if args:
            try:
                parsed_args = json.loads(args)
            except Exception:
                parsed_args = args  # если не JSON — передаём как есть
            if isinstance(parsed_args, dict):
                await func(message, **parsed_args)
            elif isinstance(parsed_args, list):
                await func(message, *parsed_args)
            else:
                await func(message, parsed_args)
        else:
            await func(message)

async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    raw_data = callback.data

    try:
        callback_data = MenuCbData.unpack(raw_data)
    except Exception:
        await callback.answer("Некорректный callback_data")
        return

    action = callback_data.action
    data = callback_data.data
    args = callback_data.args
    callback_name = callback_data.callback

    match action:
        case "goto":
            await handle_send_menu(callback.message, data, True)
        case "func":
            await handle_func_call(callback.message, data, args)
        case "input":
            await handle_func_call(callback.message, data, args)
            await state.set_state(UserStates.waitInput)
            await state.update_data({"action": action, "data": callback_name})
        case "nothing":
            ...
        case _:
            await callback.message.answer(f"⚠ Нет такого действия: {action} {data}")
    await callback.answer()

async def handle_state(message: Message, state: FSMContext):
    if not state:
        await message.answer(f"Пустое состояние")

    d = await state.get_data()
    action = d["action"]
    data = d["data"]

    match await state.get_state():
        case UserStates.waitInput:
            if action == "input":
                await handle_func_call(message, data)



def register_handlers(router: Router):
    @router.callback_query()
    async def router_handle_callback(callback: types.CallbackQuery, state: FSMContext):
        await handle_callback(callback, state)

    @router.message()
    async def router_handle_message(message: types.Message, state: FSMContext):
        await handle_state(message, state)
