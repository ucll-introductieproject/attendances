from math import ceil
from absentees.gui.grid import Grid
import pygame


class AttendancesViewer:
    def __init__(self, settings, model, rectangle):
        self.__settings = settings
        self.__model = model
        self.__ncolumns = 10
        self.__nrows = ceil(len(model.attendances.people) / self.__ncolumns)
        self.__grid = Grid(rectangle, (self.__ncolumns, self.__nrows), self.__render_person)
        self.__font = pygame.font.SysFont(None, size=24)

    def __render_person(self, surface, position, rectangle):
        pygame.draw.rect(surface, (0, 0, 0), rectangle)
        label = self.__render_label(position)
        self.__blit_label(surface, label, rectangle)

    def __render_label(self, position):
        x, y = position
        color = (255, 255, 255)
        return self.__font.render(f'{x}, {y}', True, color)

    def __blit_label(self, surface, label, rectangle):
        w, h = label.get_size()
        x = rectangle.left + (rectangle.width - w) // 2
        y = rectangle.top + (rectangle.height - h) // 2
        surface.blit(label, (x, y))

    def render(self, surface):
        self.__grid.render(surface)
