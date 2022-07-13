from absentees.animations import Animation


class FloatAnimation(Animation):
    def __init__(self, start, target, duration):
        self.__start = start
        self.__target = target
        self.__duration = duration
        self.__time = 0

    def tick(self, elapsed_seconds):
        new_time = self.__time + elapsed_seconds
        if new_time >= self.__duration:
            self.__time = self.__duration
            return new_time - self.__duration
        else:
            self.__time = new_time
            return 0

    @property
    def value(self):
        t = self.__time / self.__duration
        return self.__start + t * (self.__target - self.__start)

    @property
    def finished(self):
        return self.__time == self.__duration
