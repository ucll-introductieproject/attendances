from attendances.countdown import Countdown
import logging


class FrameViewer:
    def __init__(self, surface, position):
        self.__surface = surface
        self.__position = position
        # self.__freeze_time = 2
        # self.__countdown = Countdown(self.__freeze_time, 0)

    def tick(self, elapsed_seconds):
        pass

    def new_frame(self, image):
        self.__surface.blit(image, self.__position)

    def new_analysis(self):
        pass
