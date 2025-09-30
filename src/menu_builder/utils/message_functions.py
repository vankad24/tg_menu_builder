from aiogram.types import InputMediaPhoto, InputMediaVideo, Message

async def send_message(message: Message, text: str, keyboard=None, edit_message=False, attachment: dict | None = None):
    """
    Универсальная отправка сообщений с текстом, фото и видео.

    :param message: объект Message из aiogram
    :param text: текст сообщения
    :param keyboard: клавиатура (InlineKeyboardMarkup или ReplyKeyboardMarkup)
    :param attachment: None или кортеж (media_type, media, should_open)
                       media_type = 'photo'|'video'
                       data = путь к файлу или URL
                       should_open = True, если нужно открыть локальный файл
    :param edit_message: редактировать существующее сообщение
    """
    if attachment:
        media_type = attachment.get('type')
        media = attachment.get('data')
        should_open = attachment.get('should_open', False)

        if should_open:
            with open(media, 'rb') as f:
                await send_media(message, text, keyboard, media_type, f, edit_message)
        else:
            await send_media(message, text, keyboard, media_type, media, edit_message)
    else:
        if edit_message:
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)


async def send_media(message, text, keyboard, media_type, media, edit_message):
    """Функция для отправки фото или видео"""
    if edit_message:
        if media_type == 'photo':
            await message.edit_media(InputMediaPhoto(media=media, caption=text), reply_markup=keyboard)
        elif media_type == 'video':
            await message.edit_media(InputMediaVideo(media=media, caption=text), reply_markup=keyboard)
    else:
        if media_type == 'photo':
            await message.answer_photo(media, caption=text, reply_markup=keyboard)
        elif media_type == 'video':
            await message.answer_video(media, caption=text, reply_markup=keyboard)
