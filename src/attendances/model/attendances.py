from attendances.cells import Cell, ReadonlyWrapper
from attendances.model.person import Person
import json


class Attendances:
    def __init__(self, names):
        self.__people = {}
        for name in names:
            cell = Cell(False)
            person = Person(name, ReadonlyWrapper(cell))
            self.__people[name] = (cell, person)

    def __getitem__(self, name):
        cell, person = self.__people[name]
        return person

    @property
    def names(self):
        return self.__people.keys()

    @property
    def people(self):
        return [person for cell, person in self.__people.values()]

    def person_exists(self, id):
        return id in self.__people

    def register(self, name):
        assert name in self.__people
        cell, person = self.__people[name]
        if not cell.value:
            cell.value = True
