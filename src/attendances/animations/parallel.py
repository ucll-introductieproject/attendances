from attendances.animations import Animation


class ParallelAnimation(Animation):
    def __init__(self, animations):
        self.__animations = animations

    def tick(self, elapsed_seconds):
        return max([animation.tick(elapsed_seconds) for animation in self.__animations])
