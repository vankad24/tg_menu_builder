from abc import abstractmethod, ABC


class AbstractDataSource(ABC):
    @abstractmethod
    def get(self, key: str, default=None):
        pass