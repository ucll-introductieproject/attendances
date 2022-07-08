from tkinter import Frame
import pygame
import logging
from absentees.server import Channel, server
import cv2
import time
from absentees.countdown import Countdown
from absentees.cells import Cell
from absentees.capturer import Capturer
from absentees.face import FaceDetector
from absentees.qr import QRScanner
from absentees.gui.screens import *
from absentees.gui.clock import Clock
from absentees.repeater import Repeater
from contextlib import contextmanager



@contextmanager
def auto_capture(surface_cell, time_interval):
    camera_name = Capturer.default_camera()
    with Capturer(camera_name, surface_cell.value) as capture:
        def capture_and_refresh():
            capture()
            surface_cell.refresh()

        repeater = Repeater(capture_and_refresh, time_interval)
        yield repeater


class FrameAnalyzer:
    def __init__(self, surface_cell):
        assert isinstance(surface_cell, Cell)
        self.__surface_cell = surface_cell
        self.__pixels_cell = self.__surface_cell.derive(self.__convert_to_pixels)
        # self.__grayscale_cell = self.__pixels_cell.derive(self.__convert_to_grayscale)
        self.__qr_codes = self.__pixels_cell.derive(self.__decode_qr_codes)
        self.__qr_scanner = QRScanner()

    @property
    def surface(self):
        return self.__surface_cell

    @property
    def qr_codes(self):
        return self.__qr_codes

    def __convert_to_pixels(self, surface):
        assert isinstance(surface, pygame.Surface), f'type {type(surface)}'
        return pygame.surfarray.array3d(surface).swapaxes(0, 1)

    # def __convert_to_grayscale(self, pixels):
    #     return cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)

    def __decode_qr_codes(self, pixels):
        results = self.__qr_scanner.scan(pixels)
        if results:
            logging.debug(f'Found {len(results)} QR code(s)')
        return results


class Model:
    def __init__(self, settings):
        self.__current_frame = Cell(Model.__create_frame(settings))
        self.__analyzer = FrameAnalyzer(self.__current_frame)
        self.__qr_scan_countdown = Countdown(0.25)

    @staticmethod
    def __create_frame(settings):
        capture_size = settings['capture.width'], settings['capture.height']
        return pygame.Surface(capture_size)

    def tick(self, elapsed_seconds):
        self.__qr_scan_countdown.tick(elapsed_seconds)

    @property
    def current_frame(self):
        return self.__current_frame

    @property
    def qr_codes(self):
        return self.__analyzer.qr_codes

    # def __on_current_frame_updated(self):
    #     if self.__qr_scan_countdown.ready:
    #         self.__qr_scan_countdown.reset()
    #         self.__look_for_qr()

    # def __look_for_qr(self):
    #     image = pygame.surfarray.array3d(self.__current_frame.value).swapaxes(0, 1)
    #     if results := self.__qr_scanner.scan(image):
    #         result = results[0]
    #         highlight_color = (255, 0, 0)
    #         width = 2
    #         pygame.draw.polygon(
    #             surface=self.current_frame.value,
    #             color=highlight_color,
    #             points=result.polygon,
    #             width=width)


class FrameViewer:
    def __init__(self, model):
        self.__freeze_time = 2
        self.__countdown = Countdown(self.__freeze_time)
        self.__model = model
        self.__surface = pygame.Surface(self.__model.current_frame.value.get_size())
        self.__image_cell = Cell(self.__model.current_frame.value)
        self.__image_viewer = ImageViewer(self.__image_cell, (0, 0))
        self.__model.current_frame.add_observer(self.__on_frame_updated)

    def tick(self, elapsed_seconds):
        self.__countdown.tick(elapsed_seconds)

    def render(self, surface):
        self.__image_viewer.render(surface)

    def __on_frame_updated(self):
        if self.__model.qr_codes.value:
            self.__freeze_frame()
        elif self.__countdown.ready:
            self.__show_current_frame()

    def __freeze_frame(self):
        self.__countdown.reset()
        self.__copy_current_frame()
        self.__highlight_qr_codes()
        self.__image_cell.value = self.__surface

    def __copy_current_frame(self):
        self.__surface.blit(self.__model.current_frame.value, (0, 0))

    def __highlight_qr_codes(self):
        highlight_color = (255, 0, 0)
        for qr_code in self.__model.qr_codes.value:
            pygame.draw.polygon(self.__surface, highlight_color, qr_code.polygon, width=2)

    def __show_current_frame(self):
        self.__image_cell.value = self.__model.current_frame.value


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
    capture_fps = settings['capture.rate']
    clock = Clock(settings['frame-rate'])
    font = pygame.font.SysFont(None, settings['font-size'])
    window_size = get_window_size(settings)

    current_screen = None

    logging.debug(f'Creating window with size {window_size[0]}x{window_size[1]}')
    surface = pygame.display.set_mode(window_size)

    # capture_surface_cell = Cell(pygame.Surface((capture_width, capture_height)))
    # capture_ndarray_cell = capture_surface_cell.derive(lambda x: pygame.surfarray.array3d(x).swapaxes(0, 1))
    # capture_grayscale = capture_ndarray_cell.derive(lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY))

    # countdown = Countdown(1 / capture_fps)
    model = Model(settings)
    frame_viewer = FrameViewer(model)

    with server(channel), auto_capture(model.current_frame, 1 / 30) as auto_capturer:
        # screen_data = {
        #     'switch_screen': switch_screen,
        #     'face_detector': FaceDetector(),
        #     'qr_scanner': QRScanner(),
        #     'sound_player': sound_player,
        #     'qr_highlight_color': settings.color('qr.highlight-color'),
        #     'font': font,
        #     'capture_rate': settings['qr.capture-rate'],
        #     'freeze_time': settings['qr.freeze-time'],
        # }

        # current_screen = IdleScreen(screen_data, model.current_frame)

        clock.add_observer(model.tick)
        clock.add_observer(auto_capturer.tick)
        clock.add_observer(frame_viewer.tick)
        # clock.add_observer(countdown.tick)
        # clock.add_observer(lambda dt: current_screen.tick(dt))

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
            #         surface.blit(capture_surface.value, (0, 0))

            # current_screen.render(surface)

            frame_viewer.render(surface)
            pygame.display.flip()
