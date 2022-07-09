import pygame
import logging
import cv2
from collections import namedtuple
from absentees.server import Channel, server
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


FrameAnalysis = namedtuple('FrameAnalysis', ['qr_codes', 'faces'])

class FrameAnalyzer:
    def __init__(self):
        self.__qr_scanner = QRScanner()
        self.__face_detector = FaceDetector()

    def analyze(self, surface):
        assert isinstance(surface, pygame.Surface)
        pixels = FrameAnalyzer.__convert_to_pixels(surface)
        qr_codes = self.__qr_scanner.scan(pixels)
        if qr_codes:
            grayscale = FrameAnalyzer.__convert_to_grayscale(pixels)
            faces = self.__face_detector.detect(grayscale)
            return FrameAnalysis(qr_codes=qr_codes, faces=faces)
        else:
            return None

    def highlight_qr_code(self, surface, qr_code):
        highlight_color = (255, 0, 0)
        pygame.draw.polygon(surface, highlight_color, qr_code.polygon, width=2)

    def highlight_qr_codes(self, surface, qr_codes):
        for qr_code in qr_codes:
            self.highlight_qr_code(surface, qr_code)

    def highlight_face(self, surface, face):
        assert isinstance(surface, pygame.Surface)
        assert isinstance(face, pygame.Rect), f'is {type(face)} instead'
        highlight_color = (255, 0, 0)
        pygame.draw.rect(surface=surface, color=highlight_color, rect=face, width=2)

    def highlight_faces(self, surface, faces):
        for face in faces:
            self.highlight_face(surface, face)

    @staticmethod
    def __convert_to_pixels(surface):
        assert isinstance(surface, pygame.Surface), f'type {type(surface)}'
        return pygame.surfarray.array3d(surface).swapaxes(0, 1)

    @staticmethod
    def __convert_to_grayscale(pixels):
        return cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)


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
            logging.debug(analysis)
            logging.debug('Found QR code')
            self.__copy_current_frame()
            logging.debug('Highlighting QR codes and faces')
            self.__analyzer.highlight_qr_codes(self.__analyzed_frame, analysis.qr_codes)
            self.__analyzer.highlight_faces(self.__analyzed_frame, analysis.faces)
            self.frame_analysis.value = (self.__analyzed_frame, analysis)

    def __copy_current_frame(self):
        self.__analyzed_frame.blit(self.__current_frame.value, (0, 0))

    @property
    def frame_analysis(self):
        return self.__frame_analysis


class FrameViewer:
    def __init__(self, model):
        self.__model = model
        self.__freeze_time = 2
        self.__countdown = Countdown(self.__freeze_time, 0)
        self.__image = Cell(self.__model.current_frame.value)
        self.__image_viewer = ImageViewer(self.__image, (0, 0))
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


def run(settings, sound_player):
    pygame.init()

    channel = Channel()
    clock = Clock(settings['frame-rate'])
    window_size = get_window_size(settings)

    logging.debug(f'Creating window with size {window_size[0]}x{window_size[1]}')
    surface = pygame.display.set_mode(window_size)

    model = Model(settings)
    frame_viewer = FrameViewer(model)
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
