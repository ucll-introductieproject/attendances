from attendances.model.person import Person
import logging
import re



class Attendances:
    def __init__(self, names):
        self.__people = [Person(id=index + 1, name=name) for index, name in enumerate(names)]

    def __getitem__(self, id):
        index = id - 1
        person = self.__people[index]
        assert person.id == id

    @property
    def names(self):
        return [person.name for person in self.__people]

    @property
    def people(self):
        return self.__people

    def person_exists(self, id):
        assert isinstance(id, int)
        index = id - 1
        return 0 <= index < len(self.__people)

    def register(self, id):
        assert isinstance(id, int)
        index = id - 1
        assert 0 <= index < len(self.__people)
        person = self.__people[index]
        assert person.id == id
        if not person.present.value:
            logging.info(f'Registering {id} ({person.name})')
            person.register_attendance()
        else:
            logging.info(f'{id} ({person.name}) is already registered')

    def unregister(self, id):
        assert isinstance(id, int)
        index = id - 1
        assert 0 <= index < len(self.__people)
        person = self.__people[index]
        assert person.id == id
        if person.present.value:
            logging.info(f'Unregistering {id} ({person.name})')
            person.unregister_attendance()
        else:
            logging.info(f'{id} ({person.name}) is cannot be unregistered as they were not registered')

    def find_people_by_name(self, regex):
        return [person for person in self.__people if re.search(regex, person.name)]
