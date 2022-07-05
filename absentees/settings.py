from pathlib import Path
from functools import reduce
import logging
import json


DefaultSettings = {
    'frame-rate': 30,
    'capture-rate': 5,
    'ignore': 1000,
    'audio': {
        'theme': 'big-sur',
    },
    'capture': {
        'width': 640,
        'height': 480,
        'rate': 5
    },
    'qr': {
        'ignore-repetition-duration': 1000,
    }
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
