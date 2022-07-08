import pygame
import logging
from absentees.gui.imgview import ImageViewer
from absentees.server import Channel
from absentees.countdown import Countdown


class Sheet:
    def __init__(self, surface_size):
        self.__column_count = 5
        self.__children = [ 'magnolia', 'u0057764', *map(str, range(1, 100)) ]
        self.__surface = pygame.Surface(surface_size)
        self.__font = pygame.font.SysFont(None, 16)
        self.__child_positions = self.__determine_positions()
        self.__render_sheet()

    def __determine_positions(self):
        result = {}
        for index, child in enumerate(self.__children):
            x = index % self.__column_count
            y = index // self.__column_count
            result[child] = (x, y)
        return result

    def __render_sheet(self):
        for child in self.__children:
            self.__render_child(child)

    def __render_child(self, child):
        rect = self.__child_rectangle(child)
        pygame.draw.rect(self.__surface, color=(0, 0, 0), rect=rect)
        label_surface = self.__font.render(child, True, (255, 255, 255))
        self.__surface.blit(label_surface, (rect.left, rect.top))

    def __child_rectangle(self, child):
        px, py = self.__child_positions[child]
        child_width = self.__surface.get_width() / self.__column_count
        child_height = 24
        x = px * child_width
        y = py * child_height
        return pygame.Rect(x, y, child_width, child_height)

    def render(self, target_surface, position):
        target_surface.blit(self.__surface, position)


class Screen:
    def __init__(self, screen_data):
        self._screen_data = screen_data
        for key, value in screen_data.items():
            setattr(self, key, value)

    def _blit_centered(self, source, target):
        source_width, source_height = source.get_size()
        target_width, target_height = target.get_size()
        x = (target_width - source_width) / 2
        y = (target_height - source_height) / 2
        target.blit(source, (x, y))


class IdleScreen(Screen):
    def __init__(self, screen_data, current_frame_cell):
        super().__init__(screen_data)
        # self.__scan_countdown = Countdown(1 / self.capture_rate)
        self.__sheet = Sheet((1920, 1080))
        self.__video_viewer = ImageViewer(current_frame_cell, (0, 0))


    def tick(self, elapsed_seconds):
        # self.__scan_countdown.tick(elapsed_seconds)
        pass

    def render(self, surface):
        # if self.__scan_countdown.ready:
        #     self.__scan_countdown.reset()
        #     if results := self.qr_scanner.scan(self.capture_ndarray_cell.value):
        #         result = results[0]
        #         width = 2
        #         pygame.draw.polygon(
        #             self.capture_surface_cell.value,
        #             color=self.qr_highlight_color,
        #             points=result.polygon,
        #             width=width)
        #         self.sound_player.success()
        #         self.switch_screen(CapturedScreen(self._screen_data, result.data))

        surface.fill((0, 0, 0))
        self.__video_viewer.render(surface)
        # self.__sheet.render(surface, (0, 0))

class CapturedScreen(Screen):
    def __init__(self, screen_data, data):
        super().__init__(screen_data)
        self.__time_left = self.freeze_time
        self.__data = data

    def tick(self, elapsed_seconds):
        self.__time_left = max(0, self.__time_left - elapsed_seconds)
        if self.__time_left == 0:
            self.switch_screen(IdleScreen(self._screen_data))

    @property
    def _background_color(self):
        c = self.__time_left / self.freeze_time
        return (0, round(255 * c), 0)

    def render(self, surface):
        surface.fill(self._background_color)
        self._blit_centered(source=self.capture_surface_cell.value, target=surface)
        self.__render_data(surface)

    def __render_data(self, surface):
        text_surface = self.font.render(self.__data, True, (255, 255, 255))
        capture_width, capture_height = self.capture_surface_cell.value.get_size()
        surface_width, surface_height = surface.get_size()
        text_width, text_height = text_surface.get_size()
        x = (surface_width - text_width) / 2
        y = (3 * surface_height + capture_height) / 4 - text_height / 2
        surface.blit(text_surface, (x, y))
