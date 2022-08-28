from math import ceil
from pygame import Color
from attendances.animations.color import ColorAnimation
from attendances.animations.dirac import DiracAnimation
from attendances.animations.sequence import SequenceAnimation
from attendances.model.person import Person
from attendances.gui.grid import Grid
from attendances.cells import Cell
from attendances.animations import FloatAnimation
import pygame
from operator import attrgetter


class AttendanceSlotViewer:
    def __init__(self, *, surface, rectangle, person, font):
        assert isinstance(rectangle, pygame.Rect)
        assert isinstance(person, Person)
        assert isinstance(font, pygame.font.Font)
        self.__surface = surface
        self.__rectangle = rectangle
        self.__person = person
        self.__font = font
        self.__person.present.on_value_changed(self.__on_person_changed)
        self.__absent_background_color = pygame.Color(64, 0, 0)
        self.__present_background_color = pygame.Color(0, 64, 0)
        self.__highlight_duration = 0.5
        self.__text_color = pygame.Color(255, 255, 255)
        self.__background = Cell(self.__absent_background_color)
        self.__background.on_value_changed(self.__on_background_changed)
        self.__background_animation = None

    def __on_background_changed(self):
        self.render()

    def __on_person_changed(self):
        def remove_animation():
            self.__background_animation = None

        if self.__person.present.value == True:
            self.__background_animation = SequenceAnimation(
                ColorAnimation(
                    target=self.__background,
                    start=Color(0, 255, 0),
                    end=Color(0, 64, 0),
                    duration=self.__highlight_duration
                ),
                DiracAnimation(remove_animation)
            )
        else:
            self.__background = self.__absent_background_color
            self.__background_animation = None
        self.render()

    def render(self):
        self.__render_background()
        self.__render_name()

    def __render_background(self):
        pygame.draw.rect(self.__surface, self.__background.value, self.__rectangle)

    def __render_name(self):
        name = self.__person.name
        color = self.__text_color
        label = self.__font.render(name, True, color)
        w, h = label.get_size()
        x = self.__rectangle.left + (self.__rectangle.width - w) // 2
        y = self.__rectangle.top + (self.__rectangle.height - h) // 2
        self.__surface.blit(label, (x, y))

    def tick(self, elapsed_seconds):
        if self.__background_animation:
            self.__background_animation.tick(elapsed_seconds)
            self.render()


class EmptySlotViewer:
    def __init__(self, *, surface, rectangle):
        self.__surface = surface
        self.__rectangle = rectangle

    def render(self):
        color = (0, 0, 0)
        pygame.draw.rect(self.__surface, color, self.__rectangle)

    def tick(self, elapsed_seconds):
        pass


class AttendancesViewer:
    def __init__(self, *, surface, attendances, rectangle, ncolumns, font):
        self.__surface = surface
        self.__people = sorted(attendances.people, key=attrgetter('name'))
        self.__ncolumns = ncolumns
        self.__nrows = ceil(len(self.__people) / self.__ncolumns)
        self.__grid = Grid(rectangle, (self.__ncolumns, self.__nrows))
        self.__slots_viewers = self.__create_slot_viewers(font)

    def __create_slot_viewers(self, font):
        return [[self.__create_slot_viewer(font, (x, y)) for x in range(self.__ncolumns)] for y in range(self.__nrows)]

    def __create_slot_viewer(self, font, position):
        x, y = position
        index = x + y * self.__ncolumns
        rectangle = self.__grid.child_rectangle(position)
        if index < len(self.__people):
            person = self.__people[index]
            return AttendanceSlotViewer(surface=self.__surface, rectangle=rectangle, person=person, font=font)
        else:
            return EmptySlotViewer(surface=self.__surface, rectangle=rectangle)

    def render(self):
        for row in self.__slots_viewers:
            for viewer in row:
                viewer.render()

    def tick(self, elapsed_seconds):
        for row in self.__slots_viewers:
            for viewer in row:
                viewer.tick(elapsed_seconds)
