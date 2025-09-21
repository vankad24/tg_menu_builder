from repository.BaseRepository import BaseRepository


class MenuRepository(BaseRepository):
    def get(self, key: str):
        return self._data_source.get(key)
