from attendances.animations import Animation


class SequenceAnimation(Animation):
    def __init__(self, *children):
        self.__children = list(children)
        self.__index = 0

    def tick(self, elapsed_seconds):
        while elapsed_seconds > 0 and self.__index < len(self.__children):
            elapsed_seconds = self.__children[self.__index].tick(elapsed_seconds)
            if elapsed_seconds > 0:
                self.__index += 1
        return elapsed_seconds
