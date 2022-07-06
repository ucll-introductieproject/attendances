import pygame
import logging
import cv2
from absentees.countdown import Countdown
from absentees.cells import Cell
from absentees.capturer import Capturer
from absentees.face import FaceDetector
from absentees.qr import QRScanner


def get_window_size(settings):
    info = pygame.display.Info()
    window_width, window_height = settings['window.width'], settings['window.height']
    if window_width == 0:
        window_width = info.current_w
    if window_height == 0:
        window_height = info.current_h
    return window_width, window_height


class Screen:
    def __init__(self, screen_data):
        self._screen_data = screen_data
        for key, value in screen_data.items():
            setattr(self, key, value)


class IdleScreen(Screen):
    def tick(self, elapsed_seconds):
        pass

    def render(self, surface):
        self.capture()
        if results := self.qr_scanner.scan(self.capture_ndarray_cell.value):
            result = results[0]
            width = 2
            pygame.draw.polygon(
                self.capture_surface_cell.value,
                color=self.qr_highlight_color,
                points=result.polygon,
                width=width)
            self.sound_player.success()
            self.switch_screen(CapturedScreen(self._screen_data, result.data))

        surface.fill((0, 0, 0))
        surface.blit(self.capture_surface_cell.value, (0, 0))


class CapturedScreen(Screen):
    def __init__(self, screen_data, data):
        super().__init__(screen_data)
        self.__time_left = 2
        self.__data = data

    def tick(self, elapsed_seconds):
        self.__time_left = max(0, self.__time_left - elapsed_seconds)
        if self.__time_left == 0:
            self.switch_screen(IdleScreen(self._screen_data))

    def render(self, surface):
        surface.fill(self.successful_scan_background)
        surface.blit(self.capture_surface_cell.value, (0, 0))
        self.__render_data(surface)

    def __render_data(self, surface):
        text_surface = self.font.render(self.__data, True, (255, 255, 255))
        surface_width, surface_height = surface.get_size()
        text_width, text_height = text_surface.get_size()
        x = (surface_width - text_width) / 2
        y = (surface_height - text_height) / 2
        surface.blit(text_surface, (x, y))


def run(settings, sound_player):
    def switch_screen(screen):
        nonlocal current_screen
        current_screen = screen

    pygame.init()
    fps = settings['frame-rate']
    capture_fps = settings['capture.rate']
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, settings['font-size'])
    camera = Capturer.default_camera()
    show_video = True
    window_size = get_window_size(settings)
    capture_width, capture_height = settings['capture.width'], settings['capture.height']
    current_screen = None

    logging.debug(f'Creating window with size {window_size[0]}x{window_size[1]}')
    render_surface = pygame.display.set_mode(window_size)

    capture_surface_cell = Cell(pygame.Surface((capture_width, capture_height)))
    capture_ndarray_cell = capture_surface_cell.derive(lambda x: pygame.surfarray.array3d(x).swapaxes(0, 1))
    capture_grayscale = capture_ndarray_cell.derive(lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY))

    countdown = Countdown(1 / capture_fps)
    with Capturer(camera, capture_surface_cell) as capture:
        screen_data = {
            'switch_screen': switch_screen,
            'capture': capture,
            'face_detector': FaceDetector(),
            'qr_scanner': QRScanner(),
            'capture_surface_cell': capture_surface_cell,
            'capture_ndarray_cell': capture_ndarray_cell,
            'sound_player': sound_player,
            'qr_highlight_color': settings.color('qr.highlight-color'),
            'successful_scan_background': settings.color('qr.success-background'),
            'font': font,
        }

        current_screen = IdleScreen(screen_data)

        active = True
        while active:
            elapsed_seconds = clock.tick(fps) / 1000
            countdown.tick(elapsed_seconds)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False
                # elif event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_v:
                #         show_video = not show_video

            # if countdown.ready:
            #     countdown.reset()
            #     capture()

            #     if decoded := qr_scanner.scan(capture_ndarray.value):
            #         data = decoded[0]
            #         pygame.draw.polygon(capture_surface.value, highlight_color, data.polygon, width=2)

            #         faces = face_detector.detect(capture_grayscale.value)
            #         for (x, y, w, h) in faces:
            #             rect = pygame.Rect(x, y, w, h)
            #             pygame.draw.rect(capture_surface.value, highlight_color, rect, width=2)

            #         print(data.data)
            #         sound_player.success()

            #     if show_video:
            #         render_surface.blit(capture_surface.value, (0, 0))

            current_screen.tick(elapsed_seconds)
            current_screen.render(render_surface)

            pygame.display.flip()
