from attendances.animations import Animation


class DiracAnimation(Animation):
    def __init__(self, callback):
        self.__callback = callback

    def tick(self, elapsed_seconds):
        def do_nothing():
            pass

        self.__callback()
        self.__callback = do_nothing
        return elapsed_seconds
