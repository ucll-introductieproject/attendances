from absentees.animations import Animation


class TupleAnimation(Animation):
    def __init__(self, animations):
        self.__animations = animations

    def tick(self, elapsed_seconds):
        return max(animation.tick(elapsed_seconds) for animation in self.__animations)

    @property
    def value(self):
        return tuple(animation.value for animation in self.__animations)

    @property
    def ready(self):
        return any(animation.ready for animation in self.__animations)
