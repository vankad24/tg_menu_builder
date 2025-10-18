from ..datasource.AbstractDataSource import AbstractDataSource as ADS

class BaseRepository:
    def __init__(self, data_source: ADS):
        if not isinstance(data_source, ADS):
            raise TypeError(f"data_source должен быть экземпляром {ADS}")

        self._data_source = data_source