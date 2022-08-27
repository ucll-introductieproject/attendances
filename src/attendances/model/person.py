from attendances.cells import CellBase


class Person:
    def __init__(self, name, cell):
        assert isinstance(name, str)
        assert isinstance(cell, CellBase)
        self.__name = name
        self.__present = cell

    @property
    def name(self):
        return self.__name

    @property
    def present(self):
        return self.__present
