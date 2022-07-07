import pygame
import logging
from absentees.server import Channel, start_server
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
    def __init__(self, screen_data):
        super().__init__(screen_data)
        self.__scan_countdown = Countdown(1 / self.capture_rate)
        self.__sheet = Sheet((1920, 1080))

    def tick(self, elapsed_seconds):
        self.__scan_countdown.tick(elapsed_seconds)

    def render(self, surface):
        self.capture()

        if self.__scan_countdown.ready:
            self.__scan_countdown.reset()
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
        self.__sheet.render(surface, (0, 0))
        self._blit_centered(source=self.capture_surface_cell.value, target=surface)


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


def run(settings, sound_player):
    def switch_screen(screen):
        nonlocal current_screen
        current_screen = screen

    pygame.init()

    channel = Channel()
    shutdown_server = start_server(channel)

    try:
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
                'font': font,
                'capture_rate': settings['qr.capture-rate'],
                'freeze_time': settings['qr.freeze-time'],
            }

            current_screen = IdleScreen(screen_data)

            active = True
            while active:
                elapsed_seconds = clock.tick(fps) / 1000
                countdown.tick(elapsed_seconds)

                if channel.message_from_server_waiting:
                    logging.debug('Client receives message from server')
                    request = channel.receive_from_server()
                    print(request)
                    logging.debug('Client answers server')
                    channel.respond_to_server('ok'.encode('utf-8'))

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
    finally:
        shutdown_server()