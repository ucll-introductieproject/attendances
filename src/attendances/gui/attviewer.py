from math import ceil
from attendances.animations.dirac import DiracAnimation
from attendances.animations.sequence import SequenceAnimation
from attendances.model.person import Person
from attendances.gui.grid import Grid
from attendances.cells import Cell
from attendances.animations import FloatAnimation
import pygame
from operator import attrgetter


class AttendanceSlotViewer:
    def __init__(self, settings, rectangle, person, font):
        assert isinstance(rectangle, pygame.Rect)
        assert isinstance(person, Person)
        self.__settings = settings
        self.__rectangle = rectangle
        self.__person = person
        self.__font = font
        self.__person.present.add_observer(self.__on_person_changed)
        self.__background = Cell(self.__settings.color('colors.absent'))
        self.__dirty = True
        self.__background.add_observer(self.__on_background_changed)
        self.__background_animation = None

    def __on_background_changed(self):
        self.__dirty = True

    def __on_person_changed(self):
        def remove_animation():
            self.__background_animation = None

        self.__dirty = True
        if self.__person.present.value == True:
            cell = Cell(0)
            highlight_duration = self.__settings['highlight-duration']
            self.__background_animation = SequenceAnimation(
                FloatAnimation(target=cell, start=255, end=64, duration=highlight_duration),
                DiracAnimation(remove_animation)
            )
            cell.synchronize(self.__background, lambda g: (0, g, 0))
        else:
            self.__background = self.__settings.color('colors.absent')
            self.__background_animation = None

    def render(self, surface, force=False):
        if self.__dirty or force:
            self.__render_background(surface)
            self.__render_name(surface)
            self.__dirty = False

    def __render_background(self, surface):
        pygame.draw.rect(surface, self.__background.value, self.__rectangle)

    def __render_name(self, surface):
        name = self.__person.name
        color = self.__settings.color('colors.font')
        label = self.__font.render(name, True, color)
        w, h = label.get_size()
        x = self.__rectangle.left + (self.__rectangle.width - w) // 2
        y = self.__rectangle.top + (self.__rectangle.height - h) // 2
        surface.blit(label, (x, y))

    def tick(self, elapsed_seconds):
        if self.__background_animation:
            self.__background_animation.tick(elapsed_seconds)


class EmptySlotViewer:
    def __init__(self, rectangle):
        self.__rectangle = rectangle

    def render(self, surface):
        color = (0, 0, 0)
        pygame.draw.rect(surface, color, self.__rectangle)

    def tick(self, elapsed_seconds):
        pass


class AttendancesViewer:
    def __init__(self, settings, model, rectangle):
        self.__settings = settings
        self.__model = model
        self.__people = sorted(model.attendances.people, key=attrgetter('name'))
        self.__ncolumns = self.__settings['columns']
        self.__nrows = ceil(len(self.__people) / self.__ncolumns)
        self.__grid = Grid(rectangle, (self.__ncolumns, self.__nrows))
        self.__slots_viewers = self.__create_slot_viewers()

    def __create_slot_viewers(self):
        font = pygame.font.SysFont(None, size=self.__settings['font-size'])
        return [[self.__create_slot_viewer(font, (x, y)) for x in range(self.__ncolumns)] for y in range(self.__nrows)]

    def __create_slot_viewer(self, font, position):
        x, y = position
        index = x + y * self.__ncolumns
        rectangle = self.__grid.child_rectangle(position)
        if index < len(self.__people):
            person = self.__people[index]
            return AttendanceSlotViewer(self.__settings, rectangle, person, font)
        else:
            return EmptySlotViewer(rectangle)

    def render(self, surface):
        for row in self.__slots_viewers:
            for viewer in row:
                viewer.render(surface)

    def tick(self, elapsed_seconds):
        for row in self.__slots_viewers:
            for viewer in row:
                viewer.tick(elapsed_seconds)
