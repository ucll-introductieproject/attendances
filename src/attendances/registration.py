from pathlib import Path
from datetime import datetime


class FileRegistration:
    def __init__(self, path):
        assert isinstance(path, Path)
        self.__path = path

    def register(self, person):
        symbol = "-+"[person.present.value]
        time_string = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        string = f'{symbol} {time_string} {person.name}'
        with self.__path.open('a') as file:
            print(string, file=file)
