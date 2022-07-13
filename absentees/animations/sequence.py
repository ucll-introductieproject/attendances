from absentees.animations import Animation


class SequenceAnimation(Animation):
    def __init__(self, *children):
        self.__children = list(children)

    def tick(self, elapsed_seconds):
        while elapsed_seconds > 0 and self.__children:
            elapsed_seconds = self.__children[0].tick(elapsed_seconds)
            if elapsed_seconds > 0:
                del self.__children[0]
        return elapsed_seconds

    @property
    def ready(self):
        return len(self.__children) == 0

    @property
    def value(self):
        return self.__children[0].value
