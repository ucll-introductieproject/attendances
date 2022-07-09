from pathlib import Path
from functools import reduce
import logging
import json


DefaultSettings = {
    'frame-rate': 30,
    'font-size': 64,
    'sound': {
        'theme': 'big-sur',
    },
    'window': {
        'width': 1920,
        'height': 1080,
    },
    'capture': {
        'width': 640,
        'height': 480,
        'rate': 5,
        'dummy': True,
    },
    'qr': {
        'ignore-repetition-duration': 1000,
        'highlight-color': {
            'r': 255,
            'g': 0,
            'b': 0,
        },
        'capture-rate': 5,
        'freeze-time': 1,
    }
}


class Settings:
    def __init__(self, path):
        with open(path) as file:
            self.__data = json.loads(path.read_text())

    def __getitem__(self, key):
        parts = key.split('.')
        return reduce(lambda current, part: current[part], parts, self.__data)

    def color(self, key):
        r = self[key]['r']
        g = self[key]['g']
        b = self[key]['b']
        return (r, g, b)

    @property
    def data(self):
        return self.__data


def load_settings(path):
    if not path.exists():
        logging.info(f'Could not find {path}; generating default settings')
        path.write_text(json.dumps(DefaultSettings))
    return Settings(path)
