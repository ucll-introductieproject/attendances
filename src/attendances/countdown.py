class Countdown:
    def __init__(self, duration, initial=None):
        self.__duration = duration
        self.__time_left = duration if initial is None else initial

    def tick(self, elapsed_seconds):
        self.__time_left = max(0, self.__time_left - elapsed_seconds)

    @property
    def ready(self):
        return self.__time_left == 0

    def reset(self):
        self.__time_left = self.__duration
