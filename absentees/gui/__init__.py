import pygame
import logging
from absentees.server import Channel, server
import cv2
from absentees.countdown import Countdown
from absentees.cells import Cell
from absentees.capturer import Capturer
from absentees.face import FaceDetector
from absentees.qr import QRScanner
from absentees.gui.screens import *
from absentees.gui.clock import Clock
from contextlib import contextmanager

class Repeater:
    def __init__(self, func, time_interval):
        self.__func = func
        self.__time_interval = time_interval
        self.__time_left = self.__time_interval

    def tick(self, elapsed_seconds):
        self.__time_left -= elapsed_seconds
        while self.__time_left <= 0:
            self.__func()
            self.__time_left += self.__time_interval


@contextmanager
def auto_capture(surface_cell, time_interval):
    camera_name = Capturer.default_camera()
    with Capturer(camera_name, surface_cell.value) as capture:
        def capture_and_refresh():
            capture()
            surface_cell.refresh()

        repeater = Repeater(capture_and_refresh, time_interval)
        yield repeater


def get_window_size(settings):
    info = pygame.display.Info()
    window_width, window_height = settings['window.width'], settings['window.height']
    if window_width == 0:
        window_width = info.current_w
    if window_height == 0:
        window_height = info.current_h
    return window_width, window_height


def run(settings, sound_player):
    def switch_screen(screen):
        nonlocal current_screen
        current_screen = screen

    pygame.init()

    channel = Channel()

    with server(channel):
        capture_fps = settings['capture.rate']
        clock = Clock(settings['frame-rate'])
        font = pygame.font.SysFont(None, settings['font-size'])

        window_size = get_window_size(settings)
        capture_width, capture_height = settings['capture.width'], settings['capture.height']
        current_screen = None

        logging.debug(f'Creating window with size {window_size[0]}x{window_size[1]}')
        render_surface = pygame.display.set_mode(window_size)

        capture_surface_cell = Cell(pygame.Surface((capture_width, capture_height)))
        capture_ndarray_cell = capture_surface_cell.derive(lambda x: pygame.surfarray.array3d(x).swapaxes(0, 1))
        capture_grayscale = capture_ndarray_cell.derive(lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY))

        countdown = Countdown(1 / capture_fps)
        with auto_capture(capture_surface_cell, 1 / 30) as auto_capturer:
            screen_data = {
                'switch_screen': switch_screen,
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

            current_screen = IdleScreen(screen_data, capture_surface_cell)

            clock.add_observer(countdown.tick)
            clock.add_observer(auto_capturer.tick)
            clock.add_observer(lambda dt: current_screen.tick(dt))

            active = True
            while active:
                if channel.message_from_server_waiting:
                    logging.debug('Client receives message from server')
                    request = channel.receive_from_server()
                    print(request)
                    logging.debug('Client answers server')
                    channel.respond_to_server('ok'.encode('utf-8'))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        active = False

                clock.update()

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

                current_screen.render(render_surface)
                pygame.display.flip()
