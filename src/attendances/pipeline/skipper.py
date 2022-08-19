class SkipperNode:
    def __init__(self, n):
        self.__observers = []
        self.__n = n
        self.__count = 0

    def on_event(self, observer):
        self.__observers.append(observer)

    def perform(self, *args, **kwargs):
        self.__count += 1
        if self.__count == self.__n:
            self.__count = 0
            for observer in self.__observers:
                observer(*args, **kwargs)
