from repository.BaseRepository import BaseRepository
from datasource.AbstractDataSource import AbstractDataSource as ADS


class FunctionRepository(BaseRepository):
    def __init__(self, callback_handler_src: ADS, getter_src: ADS, gen_items_src: ADS):
        super().__init__(callback_handler_src)
        if not isinstance(callback_handler_src, ADS):
            raise TypeError(f"callback_handler_src должен быть экземпляром {ADS}")
        if not isinstance(getter_src, ADS):
            raise TypeError(f"getter_src должен быть экземпляром {ADS}")
        if not isinstance(gen_items_src, ADS):
            raise TypeError(f"gen_items_src должен быть экземпляром {ADS}")

        self.__callback_handler_src = callback_handler_src
        self.__getter_src = getter_src
        self.__gen_items_src = gen_items_src

