class CellBase:
    def __init__(self):
        self.__observers = []

    def _invalidate_observers(self):
        for observer in self.__observers:
            observer.invalidate()

    def refresh(self):
        self._invalidate_observers()

    def derive(self, func):
        result = Derived(self, func)
        self.__observers.append(result)
        return result


class Cell(CellBase):
    def __init__(self, initial_value):
        super().__init__()
        self.__value = initial_value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, v):
        self.__value = v
        self._invalidate_observers()


class Derived(CellBase):
    def __init__(self, cell, func):
        super().__init__()
        self.__cell = cell
        self.__func = func
        self.__valid = False
        self.__value = None

    @property
    def value(self):
        if not self.__valid:
            self.__value = self.__func(self.__cell.value)
            self.__valid = True
        return self.__value

    def invalidate(self):
        self.__valid = False
        self.__value = None
