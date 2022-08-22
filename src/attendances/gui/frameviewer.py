from attendances.countdown import Countdown
import logging
from pygame import Surface


class FrameViewer:
    def __init__(self, surface, position):
        self.__surface = surface
        self.__position = position
        self.__freeze_time = 1
        self.__countdown = Countdown(self.__freeze_time, 0)

    def tick(self, elapsed_seconds):
        self.__countdown.tick(elapsed_seconds)

    def new_frame(self, surface):
        assert isinstance(surface, Surface)
        if self.__countdown.ready:
            self.__surface.blit(surface, self.__position)

    def new_analysis(self, analysis):
        self.__countdown.reset()
        self.__surface.blit(analysis.image, self.__position)
