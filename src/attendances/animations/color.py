from attendances.animations import Animation
from attendances.animations.int import IntAnimation
from attendances.cells import Cell, CellBase
from pygame import Color


class ColorAnimation(Animation):
    def __init__(self, *, target, start, end, duration):
        assert isinstance(target, CellBase)
        assert isinstance(start, Color)
        assert isinstance(end, Color)
        self.__target = target
        self.__r = Cell(start.r)
        self.__g = Cell(start.g)
        self.__b = Cell(start.b)
        self.__r_animation = IntAnimation(target=self.__r, start=start.r, end=end.r, duration=duration)
        self.__g_animation = IntAnimation(target=self.__g, start=start.g, end=end.g, duration=duration)
        self.__b_animation = IntAnimation(target=self.__b, start=start.b, end=end.b, duration=duration)

    def tick(self, elapsed_seconds):
        leftover_time = self.__r_animation.tick(elapsed_seconds)
        self.__g_animation.tick(elapsed_seconds)
        self.__b_animation.tick(elapsed_seconds)
        self.__target.value = Color(self.__r.value, self.__g.value, self.__b.value)

        return leftover_time
