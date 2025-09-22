from aiogram import types

from src.menu_builder.repository.BaseRepository import BaseRepository


class AccessRepository(BaseRepository):
    def has_access(self, access_level, message: types.Message):
        access_info = self._data_source.get(access_level)
        if not access_info:
            return False
        return message.chat.id in access_info.get('ids', [])

    def get_fail_message(self, access_level):
        access_info = self._data_source.get(access_level)
        if not access_info:
            return ''
        return access_info.get('fail_message', '')
