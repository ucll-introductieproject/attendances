from attendances.animations import Animation


class FloatAnimation(Animation):
    def __init__(self, target, start, end, duration):
        self.__target = target
        self.__start = start
        self.__end = end
        self.__duration = duration
        self.__time = 0

    def tick(self, elapsed_seconds):
        new_time = self.__time + elapsed_seconds
        if new_time >= self.__duration:
            self.__time = self.__duration
            self.__target.value = self.__end
            return new_time - self.__duration
        else:
            self.__time = new_time
            self.__target.value = self.__start + (self.__end - self.__start) * self.__time / self.__duration
            return 0
