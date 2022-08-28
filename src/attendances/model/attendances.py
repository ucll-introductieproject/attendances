from attendances.cells import Cell, ReadonlyWrapper
from attendances.model.person import Person
import logging


class _Entry:
    def __init__(self, name):
        self.__cell = Cell(False)
        self.__person = Person(name, ReadonlyWrapper(self.__cell))

    @property
    def person(self):
        return self.__person

    @property
    def cell(self):
        return self.__cell


class Attendances:
    def __init__(self, names):
        self.__entries = [_Entry(name) for name in names]

    def __getitem__(self, id):
        return self.__entries[id].person

    @property
    def names(self):
        return [entry.person.name for entry in self.__entries]

    @property
    def people(self):
        return [entry.person for entry in self.__entries]

    def person_exists(self, id):
        assert isinstance(id, int)
        return 0 <= id < len(self.__entries)

    def register(self, id):
        assert isinstance(id, int)
        assert 0 <= id < len(self.__entries)
        entry = self.__entries[id]
        if not entry.cell.value:
            logging.info(f'Registering {id} ({entry.person.name})')
            entry.cell.value = True
        else:
            logging.info(f'{id} ({entry.person.name}) is already registered')
