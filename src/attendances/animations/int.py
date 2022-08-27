from attendances.animations import Animation
from attendances.animations.float import FloatAnimation
from attendances.cells import Cell


class IntAnimation(Animation):
    def __init__(self, /, target, start, end, duration):
        self.__target = target
        self.__float_cell = Cell(0)
        self.__float_cell.synchronize(self.__target, lambda f: round(f))
        self.__float_animation = FloatAnimation(target=self.__float_cell, start=start, end=end, duration=duration)

    def tick(self, elapsed_seconds):
        return self.__float_animation.tick(elapsed_seconds)
