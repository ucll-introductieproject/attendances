from pathlib import Path


class FileRegistration:
    def __init__(self, path):
        assert isinstance(path, Path)
        self.__path = path

    def register(self, id):
        with self.__path.open('a') as file:
            print(id, file=file)
