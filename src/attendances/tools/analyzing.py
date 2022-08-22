import logging
import pygame
import cv2
from collections import namedtuple
from attendances.tools.face import FaceDetector
from attendances.tools.qr import QRScanner


FrameAnalysis = namedtuple('FrameAnalysis', ['image', 'qr_codes', 'faces'])


class FrameAnalyzer:
    def __init__(self, *, qr_scanner, face_detector, highlight_qr=False):
        self.__qr_scanner = qr_scanner
        self.__face_detector = face_detector
        self.__highlight_qr = highlight_qr

    def analyze(self, image):
        pixels, qr_codes = self.__scan_for_qr_codes(image)
        if qr_codes:
            if self.__highlight_qr:
                self.highlight_qr_codes(image, qr_codes)
            faces = self.__scan_for_faces(pixels)
            return FrameAnalysis(image=image, qr_codes=qr_codes, faces=faces)
        else:
            return None

    def __scan_for_qr_codes(self, surface):
        pixels = FrameAnalyzer.__convert_to_pixels(surface)
        qr_codes = self.__qr_scanner.scan(pixels)
        return pixels, qr_codes

    def __scan_for_faces(self, pixels):
        grayscale = FrameAnalyzer.__convert_to_grayscale(pixels)
        return self.__face_detector.detect(grayscale)

    def highlight_qr_code(self, surface, qr_code):
        polygon = qr_code.polygon
        if len(polygon) < 3:
            logging.critical(f'QR polygon has only {len(polygon)} vertices')
        else:
            highlight_color = (255, 0, 0)
            pygame.draw.polygon(surface, highlight_color, qr_code.polygon, width=2)

    def highlight_qr_codes(self, surface, qr_codes):
        for qr_code in qr_codes:
            self.highlight_qr_code(surface, qr_code)

    def highlight_face(self, surface, face):
        assert isinstance(surface, pygame.Surface)
        assert isinstance(face, pygame.Rect), f'face should be pygame.Rect, is {type(face)} instead'
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
