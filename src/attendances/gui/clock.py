import pygame


class Clock:
    def __init__(self, ticks_per_second=60):
        self.__ticks_per_second = ticks_per_second
        self.__clock = pygame.time.Clock()
        self.__observers = []

    def add_observer(self, observer):
        self.__observers.append(observer)

    def update(self):
        elapsed_seconds = self.__clock.tick(self.__ticks_per_second) / 1000
        for observer in self.__observers:
            observer(elapsed_seconds)
