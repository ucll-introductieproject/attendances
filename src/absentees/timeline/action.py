class Action:
    def __init__(self, callback):
        self.__callback = callback

    def instantiate(self):
        return _ActionInstance(self.__callback)


class _ActionInstance:
    def __init__(self, callback):
        self.__callback = callback

    def tick(self, elapsed_seconds):
        self.__callback()
        return elapsed_seconds
