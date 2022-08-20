from attendances.animations.dirac import DiracAnimation
from attendances.animations.sequence import SequenceAnimation
from attendances.cells import Cell
from attendances.animations import FloatAnimation
import pygame


class Highlighter:
    def __init__(self, surface, rectangle, label):
        assert isinstance(surface, pygame.Surface)
        assert isinstance(rectangle, pygame.Rect)
        assert isinstance(label, Cell)
        self.__surface = surface
        self.__rectangle = rectangle
        self.__label = label
        self.__font = pygame.font.SysFont(None, 16)
        self.__background = Cell((0, 0, 0))
        self.__background_animation = None
        self.__label.add_observer(self.__label_updated)
        self.__background.add_observer(self.__background_updated)

    def __render_background(self):
        pygame.draw.rect(self.__surface, self.__background.value, self.__rectangle)

    def __render_label(self):
        color = (255, 255, 255)
        label = self.__font.render(self.__label.value, True, color)
        w, h = label.get_size()
        x = self.__rectangle.left + (self.__rectangle.width - w) // 2
        y = self.__rectangle.top + (self.__rectangle.height - h) // 2
        self.__surface.blit(label, (x, y))

    def __animate_highlight(self):
        def remove_animation():
            self.__background_animation = None

        cell = Cell(0)
        cell.synchronize(self.__background, lambda c: (0, c, 0))
        self.__background_animation = SequenceAnimation(
                FloatAnimation(target=cell, start=255, end=0, duration=1),
                DiracAnimation(remove_animation))

    def render(self):
        self.__render_background()
        self.__render_label()

    def tick(self, elapsed_seconds):
        if self.__background_animation:
            self.__background_animation.tick(elapsed_seconds)

    def __label_updated(self):
        self.render()

    def __background_updated(self):
        self.render()

    def highlight(self):
        self.__animate_highlight()