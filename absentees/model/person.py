from absentees.cells import Cell


class Person:
    def __init__(self, name):
        assert isinstance(name, str)
        self.__name = name
        self.__present = Cell(False)

    @property
    def name(self):
        return self.__name

    @property
    def present(self):
        return self.__present
