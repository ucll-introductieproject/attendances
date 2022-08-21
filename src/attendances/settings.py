from functools import reduce
from attendances.cells import Cell, CellBase
import logging
import json


DefaultSettingsData = {
    'font-size': 64,
    'sound': {
        'theme': 'big-sur',
        'quiet': False,
    },
    'gui': {
        'frame-rate': 0,
        'skip-rate': 5,
        'window': {
            'width': 1920,
            'height': 1080,
        },
        'show-fps': True,
        'attendances': {
            'columns': 24,
            'font-size': 16,
            'colors': {
                'absent': {
                    'r': 64,
                    'g': 0,
                    'b': 0,
                },
                'font': {
                    'r': 255,
                    'g': 255,
                    'b': 255,
                }
            },
            'highlight-duration': 0.5,
        },
    },
    'video-capturing': {
        'width': 640,
        'height': 480,
        'rate': 30,
        'dummy': False,
    },
    'qr': {
        'ignore-repetition-duration': 1000,
        'highlight-color': {
            'r': 255,
            'g': 0,
            'b': 0,
        },
        'rate': 5,
        'freeze-time': 1,
        'generation': {
            'box-size': 10,
            'border': 4,
        },
        'transformations': [
            # 'original',
            # 'bw',
            'bw_mean',
        ]
    },
    'qrtest': {
        'frame-rate': 0,
        'show-fps': True,
        'skip-rate': 5,
        'font-size': 24,
    }
}


class Settings:
    def __init__(self, data, key_prefix=[]):
        self.__data = data
        self.__key_prefix = key_prefix

    def __getitem__(self, key=''):
        parts = self.__split_key(key)
        return self.__get_cell_at(parts).value

    def __setitem__(self, key, value):
        parts = self.__split_key(key)
        self.__get_cell_at(parts).value = value

    def __get_cell_at(self, parts):
        return reduce(lambda current, part: current[part], parts, self.__data)

    def subtree(self, key):
        parts = self.__split_key(key)
        return Settings(self.__data, parts)

    def __split_key(self, key_string):
        return [*self.__key_prefix, *key_string.split('.')]

    def color(self, key):
        r = self[f'{key}.r']
        g = self[f'{key}.g']
        b = self[f'{key}.b']
        return (r, g, b)

    def size(self, key):
        width = self[f'{key}.width']
        height = self[f'{key}.height']
        return (width, height)

    @property
    def data(self):
        return _decellify(self.__data)


def _cellify(data):
    if isinstance(data, dict):
        return {key: _cellify(value) for key, value in data.items()}
    else:
        return Cell(data)


def _decellify(data):
    if isinstance(data, CellBase):
        return data.value
    elif isinstance(data, list):
        return [_decellify(x) for x in data]
    elif isinstance(data, dict):
        return {key: _decellify(value) for key, value in data.items()}
    else:
        assert False


def _create_settings_from_data(data):
    return Settings(_cellify(data))


def _create_settings_from_json(json_string):
    return _create_settings_from_data(json.loads(json_string))


def load_settings(path):
    if not path.exists():
        logging.info(f'Could not find {path}; generating default settings')
        path.write_text(json.dumps(DefaultSettingsData))
    json_string = path.read_text()
    return _create_settings_from_json(json_string)


def default_settings():
    return _create_settings_from_data(DefaultSettingsData)
