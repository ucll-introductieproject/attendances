from math import ceil
from absentees.gui.grid import Grid
import pygame
from operator import attrgetter


class AttendanceSlotViewer:
    def __init__(self, model, rectangle, name, font):
        self.__model = model
        self.__rectangle = rectangle
        self.__name = name
        self.__font = font

    def render(self, surface):
        self.__render_background(surface)
        self.__render_name(surface)

    def __render_background(self, surface):
        pygame.draw.rect(surface, self.__background_color, self.__rectangle)

    def __render_name(self, surface):
        name = self.__person.name
        color = (255, 255, 255)
        label = self.__font.render(name, True, color)
        w, h = label.get_size()
        x = self.__rectangle.left + (self.__rectangle.width - w) // 2
        y = self.__rectangle.top + (self.__rectangle.height - h) // 2
        surface.blit(label, (x, y))

    @property
    def __background_color(self):
        if self.__person.present:
            return (0, 64, 0)
        else:
            return (64, 0, 0)

    @property
    def __person(self):
        return self.__model.attendances[self.__name]


class EmptySlotViewer:
    def __init__(self, rectangle):
        self.__rectangle = rectangle

    def render(self, surface):
        color = (0, 0, 0)
        pygame.draw.rect(surface, color, self.__rectangle)


class AttendancesViewer:
    def __init__(self, settings, model, rectangle):
        self.__settings = settings
        self.__model = model
        self.__people = sorted(model.attendances.people, key=attrgetter('name'))
        self.__ncolumns = 10
        self.__nrows = ceil(len(self.__people) / self.__ncolumns)
        self.__grid = Grid(rectangle, (self.__ncolumns, self.__nrows))
        self.__slots_viewers = self.__create_slot_viewers()

    def __create_slot_viewers(self):
        font = pygame.font.SysFont(None, size=24)
        return [[self.__create_slot_viewer(font, (x, y)) for x in range(self.__ncolumns)] for y in range(self.__nrows)]

    def __create_slot_viewer(self, font, position):
        x, y = position
        index = x + y * self.__ncolumns
        rectangle = self.__grid.child_rectangle(position)
        if index < len(self.__people):
            person = self.__people[index]
            return AttendanceSlotViewer(self.__model, rectangle, person.name, font)
        else:
            return EmptySlotViewer(rectangle)

    def render(self, surface):
        for row in self.__slots_viewers:
            for viewer in row:
                viewer.render(surface)
