import logging
import pygame
from attendances.capturers import InjectingCapturer
from attendances.cells import Cell
from attendances.model.attendances import Attendances
from attendances.timeline import repeat, Parallel


class Model:
    def __init__(self, settings, video_capturer, frame_analyzer, names):
        self.__settings = settings
        self.__current_frame = Cell(Model.__create_surface(settings))
        self.__analyzed_frame = Model.__create_surface(settings)
        self.__frame_analysis = Cell(None)
        self.__analyzer = frame_analyzer
        self.__attendances = Attendances(names)
        self.__video_capturer = InjectingCapturer(video_capturer)
        self.__timeline = self.__create_timeline()
        self.__active = False

    def __create_timeline(self):
        capturing_timeline = repeat(self.__capture_frame, 1/self.__settings['video-capturing.rate'])
        analysis_timeline = repeat(self.__analyze_current_frame, 1/self.__settings['qr.rate'])
        return Parallel(capturing_timeline, analysis_timeline).instantiate()

    def __capture_frame(self):
        self.__video_capturer.capture(self.__current_frame.value)

    def __enter__(self):
        self.__video_capturer.__enter__()
        self.__active = True

    def __exit__(self, exception, value, traceback):
        self.__active = False
        self.__video_capturer.__exit__(exception, value, traceback)

    def tick(self, elapsed_seconds):
        if self.__active:
            self.__timeline.tick(elapsed_seconds)

    @property
    def video_capturer(self):
        return self.__video_capturer

    @property
    def attendances(self):
        return self.__attendances

    @staticmethod
    def __create_surface(settings):
        capture_size = settings['video-capturing.width'], settings['video-capturing.height']
        return pygame.Surface(capture_size)

    @property
    def current_frame(self):
        return self.__current_frame

    def __analyze_current_frame(self):
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
