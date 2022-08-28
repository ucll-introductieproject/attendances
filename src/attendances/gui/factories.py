import logging
import pygame
import json
from attendances.cells import Cell
from attendances.gui.attviewer import AttendancesViewer
from attendances.gui.clock import Clock
from attendances.gui.frameviewer import FrameViewer
from attendances.model.attendances import Attendances
from attendances.server import Channel, server
from attendances.pipeline import *
import attendances.commands as commands
from attendances.tools.analyzing import FrameAnalyzer
from attendances.tools.capturing import DummyCapturer, VideoCapturer
from attendances.tools.face import NullFaceDetector
from attendances.tools.qr import QRScanner
from attendances.tools.sound import SoundPlayer
import attendances.settings as settings



def create_capturer(settings):
    if settings['dummy']:
        logging.info('Creating dummy capturer')
        return DummyCapturer()
    else:
        size = (settings['width'], settings['height'])
        logging.info(f'Creating video capturer with size {size}')
        return VideoCapturer.default_camera(size)


def create_frame_analyzer(settings):
    logging.info("Creating frame analyzer")
    qr_scanner = QRScanner()
    face_detector = NullFaceDetector()
    return FrameAnalyzer(qr_scanner=qr_scanner, face_detector=face_detector)


def create_clock(settings):
    rate = settings['frame-rate']
    logging.info(f'Creating clock with rate {rate}')
    return Clock(rate)


def create_window():
    width, height = size = settings.gui.window_size
    logging.info(f'Creating window with size {width}x{height}')
    return pygame.display.set_mode(size)


def create_sound_player(settings):
    logging.info('Creating sound player')
    return SoundPlayer(settings['theme'], quiet=settings['quiet'])


def create_frame_viewer(surface, frame_size):
    window_width, window_height = surface.get_size()
    frame_width, frame_height = frame_size
    x = (window_width - frame_width) // 2
    y = 0
    return FrameViewer(surface, (x, y))


def create_attendances_viewer(settings, model, window_size):
    window_width, window_height = window_size
    rect = pygame.Rect(0, 480, window_width, window_height - 480)
    return AttendancesViewer(settings, model, rect)
