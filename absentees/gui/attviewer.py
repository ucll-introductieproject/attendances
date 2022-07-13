from math import ceil
from absentees.model.person import Person
from absentees.gui.grid import Grid
from absentees.animations import ConstantAnimation, Animation, TupleAnimation, FloatAnimation
import pygame
from operator import attrgetter


class AttendanceSlotViewer:
    def __init__(self, rectangle, person, font):
        assert isinstance(rectangle, pygame.Rect)
        assert isinstance(person, Person)
        self.__rectangle = rectangle
        self.__person = person
        self.__font = font
        self.__person.present.add_observer(self.__on_person_changed)
        self.__background = (64, 0, 0)
        self.__dirty = True

    def __on_person_changed(self):
        self.__dirty = True
        if self.__person.present.value == True:
            r_animation = ConstantAnimation(0)
            g_animation = FloatAnimation(255, 64, 0.25)
            b_animation = ConstantAnimation(0)
            color_animation = TupleAnimation((r_animation, g_animation, b_animation))
            self.__background = color_animation
        else:
            self.__background = ConstantAnimation((64, 0, 0))

    def render(self, surface, force=False):
        if self.__dirty or force:
            self.__render_background(surface)
            self.__render_name(surface)
            self.__dirty = False

    def __render_background(self, surface):
        color = self.__background.value if isinstance(self.__background, Animation) else self.__background
        pygame.draw.rect(surface, color, self.__rectangle)

    def __render_name(self, surface):
        name = self.__person.name
        color = (255, 255, 255)
        label = self.__font.render(name, True, color)
        w, h = label.get_size()
        x = self.__rectangle.left + (self.__rectangle.width - w) // 2
        y = self.__rectangle.top + (self.__rectangle.height - h) // 2
        surface.blit(label, (x, y))

    def tick(self, elapsed_seconds):
        if isinstance(self.__background, Animation):
            self.__background.tick(elapsed_seconds)
            self.__dirty = True


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
            return AttendanceSlotViewer(rectangle, person, font)
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
