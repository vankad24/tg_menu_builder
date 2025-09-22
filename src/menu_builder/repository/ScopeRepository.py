from string import Template

from src.menu_builder.data.Scope import Scope
from src.menu_builder.repository.BaseRepository import BaseRepository


class ScopeRepository(BaseRepository):

    def get_reserved_var(self, scope: Scope, key: str):
        get_var_func = self._data_source.get(key)
        if get_var_func and scope.message is not None:
            return get_var_func(scope.message)
        return None


def substitute_vars(text: str, scope) -> str:
    return Template(text).safe_substitute(scope)
