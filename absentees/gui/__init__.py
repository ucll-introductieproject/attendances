import pygame
import logging
from absentees.server import Channel, server
from absentees.sound import SoundPlayer
from absentees.countdown import Countdown
from absentees.cells import Cell
from absentees.capturer import Capturer
from absentees.gui.screens import *
from absentees.gui.clock import Clock
from absentees.repeater import Repeater
from absentees.analyzer import FrameAnalyzer
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


class Model:
    def __init__(self, settings):
        self.__current_frame = Cell(Model.__create_surface(settings))
        self.__analyzed_frame = Model.__create_surface(settings)
        self.__frame_analysis = Cell(None)
        self.__analyzer = FrameAnalyzer()

    @staticmethod
    def __create_surface(settings):
        capture_size = settings['capture.width'], settings['capture.height']
        return pygame.Surface(capture_size)

    @property
    def current_frame(self):
        return self.__current_frame

    def analyze_current_frame(self):
        if analysis := self.__analyzer.analyze(self.current_frame.value):
            logging.debug(f'Found QR codes: {analysis}')
            self.__copy_current_frame()
            self.__analyzer.highlight_qr_codes(self.__analyzed_frame, analysis.qr_codes)
            self.__analyzer.highlight_faces(self.__analyzed_frame, analysis.faces)
            self.frame_analysis.value = (self.__analyzed_frame, analysis)

    def __copy_current_frame(self):
        self.__analyzed_frame.blit(self.__current_frame.value, (0, 0))

    @property
    def frame_analysis(self):
        return self.__frame_analysis


class FrameViewer:
    def __init__(self, model, position):
        self.__model = model
        self.__freeze_time = 2
        self.__countdown = Countdown(self.__freeze_time, 0)
        self.__image = Cell(self.__model.current_frame.value)
        self.__image_viewer = ImageViewer(self.__image, position)
        self.__model.frame_analysis.add_observer(self.__on_new_frame_analysis)

    def tick(self, elapsed_seconds):
        self.__countdown.tick(elapsed_seconds)
        if self.__countdown.ready:
            self.__image.value = self.__model.current_frame.value

    def render(self, surface):
        self.__image_viewer.render(surface)

    def __on_new_frame_analysis(self):
        self.__countdown.reset()
        self.__image.value = self.__model.frame_analysis.value[0]


def get_window_size(settings):
    info = pygame.display.Info()
    window_width, window_height = settings['window.width'], settings['window.height']
    if window_width == 0:
        window_width = info.current_w
    if window_height == 0:
        window_height = info.current_h
    return window_width, window_height


def create_clock(settings):
    rate = settings['frame-rate']
    logging.info(f'Creating clock with rate {rate}')
    return Clock(rate)


def create_window(window_size):
    logging.info(f'Creating window with size {window_size[0]}x{window_size[1]}')
    return pygame.display.set_mode(window_size)


def create_sound_player(settings, quiet):
    logging.info('Creating sound player')
    return SoundPlayer(settings['sound.theme'], quiet=quiet)


def create_frame_viewer(model, window_size):
    window_width, window_height = window_size
    frame_width, frame_height = model.current_frame.value.get_size()
    x = (window_width - frame_width) // 2
    y = 0
    return FrameViewer(model, (x, y))


def run(settings, quiet):
    pygame.init()

    channel = Channel()
    clock = create_clock(settings)
    window_size = get_window_size(settings)
    surface = create_window(window_size)
    sound_player = create_sound_player(settings, quiet)

    model = Model(settings)
    frame_viewer = create_frame_viewer(model, window_size)
    analysis_repeater = Repeater(model.analyze_current_frame, settings['qr.capture-rate'])

    with server(channel), auto_capture(model.current_frame, 1 / 30) as auto_capturer:
        clock.add_observer(auto_capturer.tick)
        clock.add_observer(frame_viewer.tick)
        clock.add_observer(analysis_repeater.tick)

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

            frame_viewer.render(surface)
            pygame.display.flip()
