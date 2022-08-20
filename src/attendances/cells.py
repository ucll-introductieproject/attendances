class CellBase:
    def __init__(self):
        self.__observers = []

    def _notify_observers(self):
        for observer in self.__observers:
            observer()

    def on_value_changed(self, func):
        self.__observers.append(func)

    def refresh(self):
        self._notify_observers()

    def derive(self, func, /, lazy=False):
        return (LazyDerived if lazy else StrictDerived)(self, func)

    def synchronize(self, target, func):
        def syncer():
            target.value = func(self.value)
        self.on_value_changed(syncer)

    def __str__(self):
        return f"Cell({self.value})"

    def __repr__(self):
        return f"Cell({self.value})"


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
        self._notify_observers()

    def update(self, f):
        self.__value = f(self.__value)


class LazyDerived(CellBase):
    def __init__(self, cell, func):
        super().__init__()
        self.__cell = cell
        self.__func = func
        self.__valid = False
        self.__value = None
        self.__cell.on_value_changed(self.__invalidate)

    @property
    def value(self):
        if not self.__valid:
            self.__value = self.__func(self.__cell.value)
            self.__valid = True
        return self.__value

    def __invalidate(self):
        self.__valid = False
        self.__value = None
        self._notify_observers()


class StrictDerived(CellBase):
    def __init__(self, cell, func):
        super().__init__()
        self.__cell = cell
        self.__func = func
        self.__value = func(self.__cell.value)
        self.__cell.on_value_changed(self.__refresh)

    @property
    def value(self):
        return self.__value

    def __refresh(self):
        self.__value = self.__func(self.__cell.value)
        self._notify_observers()
