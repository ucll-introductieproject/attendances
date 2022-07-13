from absentees.model.person import Person


class Attendances:
    def __init__(self, names):
        self.__people = {name: Person(name) for name in names}

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
