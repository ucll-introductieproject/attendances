from attendances.cells import Cell, ReadonlyWrapper


class Person:
    def __init__(self, *, id, name):
        assert isinstance(id, int)
        assert isinstance(name, str)
        self.__id = id
        self.__name = name
        self.__present = Cell(False)
        self.__wrapper = ReadonlyWrapper(self.__present)

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def present(self):
        return self.__wrapper

    def register_attendance(self):
        self.__present.value = True

    def unregister_attendance(self):
        self.__present.value = False
