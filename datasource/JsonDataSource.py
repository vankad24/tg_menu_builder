import json
import os

from datasource.AbstractDataSource import AbstractDataSource


class JsonDataSource(AbstractDataSource):
    def __init__(self, path: str):
        self.path = os.path.abspath(path.strip())

        if not self.path or not os.path.exists(self.path):
            raise FileNotFoundError(f"Файл не найден: {self.path}")

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self._data: dict = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(
                f"Ошибка декодирования JSON в файле: {self.path}. Убедитесь, что файл содержит валидный JSON.")
        except Exception as e:
            raise RuntimeError(f"Непредвиденная ошибка при чтении файла {self.path}: {e}")

    def get(self, key: str, default=None):
        return self._data.get(key, default)