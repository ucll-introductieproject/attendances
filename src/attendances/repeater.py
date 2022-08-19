class Repeater:
    def __init__(self, func, time_interval):
        self.__func = func
        self.__time_interval = time_interval
        self.__time_left = self.__time_interval

    def tick(self, elapsed_seconds):
        self.__time_left -= elapsed_seconds
        while self.__time_left <= 0:
            self.__func()
            self.__time_left += self.__time_interval
