import logging
import pygame
from absentees.cells import Cell
from absentees.analyzer import FrameAnalyzer
from absentees.model.attendances import Attendances


class Model:
    def __init__(self, settings, names):
        self.__current_frame = Cell(Model.__create_surface(settings))
        self.__analyzed_frame = Model.__create_surface(settings)
        self.__frame_analysis = Cell(None)
        self.__analyzer = FrameAnalyzer()
        self.__attendances = Attendances(names)

    @property
    def attendances(self):
        return self.__attendances

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
