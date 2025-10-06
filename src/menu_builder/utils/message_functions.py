from typing import Union

from aiogram.types import (
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    FSInputFile
)

def get_input_media(attachment: list[dict] | dict, text: str):

    is_list = isinstance(attachment, list)
    result = []

    if not is_list:
        attachment=[attachment]

    for idx, item in enumerate(attachment):
        media_type = item.get("type")
        data = item.get("data")
        should_open = item.get("should_open", False)
        has_spoiler = item.get("has_spoiler", False)

        # todo ??? caption = text if idx == 0 else None  # caption = text только у первого

        if should_open:
            data = FSInputFile(data)

        if media_type == "photo":
            result.append(InputMediaPhoto(media=data, caption=text, has_spoiler=has_spoiler))
        elif media_type == "video":
            result.append(InputMediaVideo(media=data, caption=text, has_spoiler=has_spoiler))
    if not is_list:
        result = result[0]
    return result



async def send_message(
        message: Message,
        text: str = "",
        keyboard=None,
        attachment: Union[dict, list[dict], None] = None,
        edit_message: bool = False,
        protect_content: bool = False,
):
    """
    Универсальная отправка сообщений с текстом, фото и видео.

    attachment:
        dict или list[dict], где dict имеет поля:
        - type: 'photo'|'video'
        - data: путь к файлу или URL
        - should_open: bool (открыть файл локально)
        - has_spoiler: bool (наложить спойлер на фото/видео)
    """
    if not attachment:
        return await send_text(message, text, keyboard, edit_message, protect_content)
    elif isinstance(attachment, dict):
        return await send_media(message, attachment, text, keyboard, edit_message, protect_content)
    elif isinstance(attachment, list):
        return await send_media_group(message, attachment, text, keyboard, edit_message, protect_content)

async def send_text(
        message: Message,
        text: str = "",
        keyboard=None,
        edit_message: bool = False,
        protect_content: bool = False,
):
    if edit_message and message.content_type != "text":
        await message.delete()
        edit_message = False

    if edit_message:
        result = await message.edit_text(text, reply_markup=keyboard, protect_content=protect_content)
    else:
        result = await message.answer(text, reply_markup=keyboard, protect_content=protect_content)
    return result

async def send_media(message, attachment, text, keyboard, edit_message=False, protect_content=False):
    """Функция для отправки/редактирования одного фото или видео"""
    media = get_input_media(attachment, text)

    if edit_message and message.content_type == "text":
        await message.delete()
        edit_message = False

    if edit_message:
        return await message.edit_media(media, reply_markup=keyboard, protect_content=protect_content)
    else:
        func = None
        match attachment['type']:
            case 'photo':
                func = message.answer_photo
            case 'video':
                func = message.answer_video

        if not func:
            return None
        return await func(media.media, caption=text, reply_markup=keyboard, has_spoiler=media.has_spoiler, protect_content=protect_content)

async def send_media_group(message: Message, attachments: list, text: str, keyboard, edit_message=False, protect_content=False):
    """Отправка нескольких фото/видео"""
    media = get_input_media(attachments, text)

    if edit_message:
        await message.delete()

    result = await message.answer_media_group(media=media, protect_content=protect_content)

    if keyboard:
        # клавиатуру придётся отправить отдельным сообщением
        await message.answer("⬆️ Медиа выше", reply_markup=keyboard)
    return result