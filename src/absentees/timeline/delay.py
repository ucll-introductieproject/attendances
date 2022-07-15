class Delay:
    def __init__(self, duration):
        self.__duration = duration

    def instantiate(self):
        return _DelayInstance(self.__duration)


class _DelayInstance:
    def __init__(self, duration):
        self.__time_left = duration

    def tick(self, elapsed_seconds):
        if self.__time_left > elapsed_seconds:
            self.__time_left -= elapsed_seconds
            return 0
        else:
            result = elapsed_seconds - self.__time_left
            self.__time_left = 0
            return result
