from absentees.animations import Animation


class ConstantAnimation(Animation):
    def __init__(self, constant):
        self.__constant = constant

    def tick(self, elapsed_seconds):
        return 0

    @property
    def value(self):
        return self.__constant

    @property
    def ready(self):
        return False
