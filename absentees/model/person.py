class Person:
    def __init__(self, name):
        assert isinstance(name, str)
        self.__name = name
        self.__present = False

    @property
    def name(self):
        return self.__name

    @property
    def present(self):
        return self.__present

    @present.setter
    def present(self, value):
        self.__present = value
