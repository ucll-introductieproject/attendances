from absentees.model.person import Person
import json


class Attendances:
    def __init__(self, names):
        self.__people = {}
        for name in names:
            person = Person(name)
            self.__people[name] = person
            person.present.add_observer(self.__on_person_changed)
        self.__write_to_file()

    def __getitem__(self, name):
        return self.__people[name]

    @property
    def names(self):
        return self.__people.keys()

    @property
    def people(self):
        return self.__people.values()

    def register(self, name):
        self.__people[name].present.value = True

    def __on_person_changed(self):
        self.__write_to_file()

    def __write_to_file(self):
        with open('attendances.txt', 'w') as file:
            data = {person.name: person.present.value for person in self.people}
            json.dump(data, file)
