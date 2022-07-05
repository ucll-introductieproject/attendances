from pathlib import Path
from functools import reduce
import logging
import json


DefaultSettings = {
    'frame_rate': 30,
    'capture_rate': 5,
}


class Settings:
    def __init__(self, path):
        with open(path) as file:
            self.__data = json.loads(path.read_text())

    def __getitem__(self, key):
        parts = key.split('.')
        return reduce(lambda current, part: current[part], parts, self.__data)

    @property
    def data(self):
        return self.__data


def load_settings(path):
    if not path.exists():
        logging.info(f'Could not find {path}; generating default settings')
        path.write_text(json.dumps(DefaultSettings))
    return Settings(path)
