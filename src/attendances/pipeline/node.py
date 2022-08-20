class Node:
    def __init__(self):
        self.__observers = []

    def _notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer(*args, **kwargs)

    def link(self, observer):
        self.__observers.append(observer)
