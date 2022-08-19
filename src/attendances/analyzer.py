import pygame
import cv2
from collections import namedtuple
from attendances.face import FaceDetector
from attendances.qr import QRScanner


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
