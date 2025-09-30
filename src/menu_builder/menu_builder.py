import json

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from .data.MenuCbData import MenuCbData
from .data.RepositoryStorage import RepositoryStorage
from .data.Scope import Scope
from .data.UserStates import UserStates
from .repository.AccessRepository import AccessRepository
from .repository.FunctionRepository import FunctionRepository, handle_func_call, async_handle_func_call
from .repository.MenuRepository import MenuRepository
from .repository.ScopeRepository import ScopeRepository, substitute_vars
from .repository.TranslationRepository import TranslationRepository
from .utils.message_functions import send_message

rs: RepositoryStorage = None

def createRepositoryStorage(
        function_src,
        translation_src,
        reserved_vars_src,
        access_levels_src,
        menu_structure_src
):
    global rs
    rs = RepositoryStorage(
        funRep=FunctionRepository(function_src),
        transRep=TranslationRepository(translation_src),
        scopeRep=ScopeRepository(reserved_vars_src),
        accessRep=AccessRepository(access_levels_src),
        menuRep=MenuRepository(menu_structure_src)
    )


# ===== Генерация клавиатуры =====
def build_keyboard(message: Message, menu_item, scope) -> InlineKeyboardMarkup| None:
    buttons = menu_item.get("buttons", None)
    if not buttons:
        return None
    buttons_list = process_source(buttons, message, scope)
    buttons_list = [x if isinstance(x, list) else [x] for x in buttons_list]
    return InlineKeyboardMarkup(inline_keyboard=buttons_list)

async def get_attachment(message: Message, menu_item, scope):
    attachment_item = menu_item.get("attachment", None)
    if not attachment_item:
        return None
    a_type = gfm(attachment_item, 'type', scope)
    data = gfm(attachment_item, 'data', scope)

    match a_type:
        case 'func':
            args = parse_args(attachment_item, scope)
            func = rs.funRep.get_functon(data)
            return await async_handle_func_call(message, func, args)
        case 'photo' | 'video':
            should_open = attachment_item['should_open']
            return {'type': a_type, 'data': data, 'should_open': should_open}
    return None

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

def parse_args(item, scope):
    args = None
    if "args" in item:
        arr = [
            substitute_vars(x, scope) if isinstance(x, str) else x
            for x in item["args"]
        ]
        args = json.dumps(arr)
    return args

# get from item
def gfm(item, name, scope):
    return substitute_vars(item[name], scope)

def process_item(item, message: Message, parent_scope):
    scope = load_scope(item, parent_scope, message)

    access, fail_message = has_access(message, item, scope)
    if not access:
        return None

    action = substitute_vars(item["action"], scope)
    match action:
        case "goto":
            return InlineKeyboardButton(
                text=rs.transRep.process_text(item, scope),
                callback_data=MenuCbData(action="goto", data=substitute_vars(item["data"], scope)).pack()
            )
        case "func":
            return InlineKeyboardButton(
                text=rs.transRep.process_text(item, scope),
                callback_data=MenuCbData(
                    action="func",
                    data=substitute_vars(item["data"], scope),
                    args=parse_args(item, scope)
                ).pack()
            )
        case "gen":
            func = rs.funRep.get_functon(substitute_vars(item["data"], scope))
            var_dicts = handle_func_call(message, func)
            pattern_item = item["pattern"]

            buttons = []
            for var_dict in var_dicts:
                buttons.extend(process_source([pattern_item], message, Scope(var_dict, scope)))
            return buttons

        case "gen_manual":
            func = rs.funRep.get_functon(substitute_vars(item["data"], scope))
            items = handle_func_call(message, func)
            return process_source(items, message, scope)
        case "input":
            return InlineKeyboardButton(
                text=rs.transRep.process_text(item, scope),
                callback_data=MenuCbData(
                    action="input",
                    data=substitute_vars(item["data"], scope),
                    callback=substitute_vars(item["callback"], scope)
                ).pack()
            )
        case "nothing":
            return InlineKeyboardButton(text=rs.transRep.process_text(item, scope), callback_data=MenuCbData(action="nothing").pack())

        case _:
            raise Exception(f"Нет такого действия: {item['action']}")


def load_scope(item, parent_scope, message):
    if 'getter' in item:
        func = rs.funRep.get_functon(substitute_vars(item["getter"], parent_scope))
        vars_dict = handle_func_call(message, func)
        return Scope(vars_dict, parent_scope)
    return parent_scope

def has_access(message: types.Message, item, scope: Scope):
    if "access" in item:
        access_level = substitute_vars(item["access"], scope)
        if not rs.accessRep.has_access(access_level, message):
            fail_message = rs.accessRep.get_fail_message(access_level)
            if fail_message:
                return False, fail_message
            return False, None
    return True, None

async def build_message(message: types.Message, menu_item, stage_scope):
    return rs.transRep.process_text(menu_item, stage_scope), build_keyboard(message, menu_item, stage_scope), await get_attachment(message, menu_item, stage_scope)

async def handle_send_menu(message: types.Message, menu_key: str, edit_message=False):
    menu_item = rs.menuRep.get(menu_key)
    stage_scope = load_scope(menu_item, Scope({}, message=message, scopeRep=rs.scopeRep), message)

    #check access level
    access, fail_message = has_access(message, menu_item, stage_scope)
    if not access:
        if fail_message:
            await message.answer(fail_message)
        return

    msg_text, keyboard, attachment = await build_message(message, menu_item, stage_scope)
    if msg_text:
        await send_message(message, msg_text, keyboard, edit_message, attachment)


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
            func = rs.funRep.get_functon(data)
            await async_handle_func_call(callback.message, func, args)
        case "input":
            func = rs.funRep.get_functon(data)
            await async_handle_func_call(callback.message, func, args)
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
                func = rs.funRep.get_functon(data)
                await async_handle_func_call(message, func)


def register_handlers(router: Router):
    @router.callback_query()
    async def router_handle_callback(callback: types.CallbackQuery, state: FSMContext):
        await handle_callback(callback, state)

    @router.message()
    async def router_handle_message(message: types.Message, state: FSMContext):
        await handle_state(message, state)
