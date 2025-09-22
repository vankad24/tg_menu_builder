from src.menu_builder.repository.BaseRepository import BaseRepository
from src.menu_builder.repository.ScopeRepository import substitute_vars


class TranslationRepository(BaseRepository):
    _translation_symbol_prefix = '@'

    def get_translation(self, key: str):
        return self._data_source.get(key[1:], key)

    def process_text(self, item, scope):
        if 'text' not in item:
            return ''
        text = item['text']
        if text[0] == self._translation_symbol_prefix:
            text = self.get_translation(text)
        return substitute_vars(text, scope)
