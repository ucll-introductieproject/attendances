from math import ceil
from turtle import back
from absentees.gui.grid import Grid
import pygame
from operator import attrgetter


class AttendancesViewer:
    def __init__(self, settings, model, rectangle):
        self.__settings = settings
        self.__model = model
        self.__people = sorted(model.attendances.people, key=attrgetter('name'))
        self.__ncolumns = 10
        self.__nrows = ceil(len(self.__people) / self.__ncolumns)
        self.__grid = Grid(rectangle, (self.__ncolumns, self.__nrows), self.__render_slot)
        self.__font = pygame.font.SysFont(None, size=24)

    def __render_slot(self, surface, position, rectangle):
        person = self.__person_at(position)
        if person:
            self.__render_person(surface, person, rectangle)
        else:
            self.__render_unused_slot(surface, rectangle)

    def __render_person(self, surface, person, rectangle):
        background_color = (0, 128, 0) if person.present else (64, 0, 0)
        self.__render_background(surface, rectangle, background_color)
        self.__render_label(surface, rectangle, person.name)

    def __render_unused_slot(self, surface, rectangle):
        color = (0, 0, 0)
        pygame.draw.rect(surface, color, rectangle)

    def __render_background(self, surface, rectangle, color):
        pygame.draw.rect(surface, color, rectangle)

    def __render_label(self, surface, rectangle, text):
        assert isinstance(surface, pygame.Surface)
        assert isinstance(rectangle, pygame.Rect)
        assert isinstance(text, str), str(type(text))
        color = (255, 255, 255)
        label = self.__font.render(text, True, color)
        w, h = label.get_size()
        x = rectangle.left + (rectangle.width - w) // 2
        y = rectangle.top + (rectangle.height - h) // 2
        surface.blit(label, (x, y))

    def render(self, surface):
        self.__grid.render(surface)

    def __person_at(self, position):
        x, y = position
        index = x + y * self.__ncolumns
        if index < len(self.__people):
            return self.__people[index]
        else:
            return None
