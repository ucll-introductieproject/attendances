from attendances.cells import Cell, ReadonlyWrapper
from attendances.model.person import Person
import logging
import re



class Attendances:
    def __init__(self, names):
        self.__people = [Person(id=index, name=name) for index, name in enumerate(names)]

    def __getitem__(self, id):
        return self.__people[id]

    @property
    def names(self):
        return [person.name for person in self.__people]

    @property
    def people(self):
        return self.__people

    def person_exists(self, id):
        assert isinstance(id, int)
        return 0 <= id < len(self.__people)

    def register(self, id):
        assert isinstance(id, int)
        assert 0 <= id < len(self.__people)
        person = self.__people[id]
        if not person.present.value:
            logging.info(f'Registering {id} ({person.name})')
            person.register_attendance()
        else:
            logging.info(f'{id} ({person.name}) is already registered')

    def find_people_by_name(self, regex):
        return [person for person in self.__people if re.search(regex, person.name)]
