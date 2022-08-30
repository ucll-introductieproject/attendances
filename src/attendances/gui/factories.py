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
from attendances.settings import settings


def create_window(width, height):
    logging.info(f'Creating window with size {width}x{height}')
    return pygame.display.set_mode((width, height))


def create_dummy_capturer():
    logging.info('Creating dummy capturer')
    return DummyCapturer()


def create_camera_capturer(width, height):
    logging.info(f'Creating video capturer with size {width}x{height}')
    return VideoCapturer.default_camera((width, height))


def create_frame_analyzer():
    logging.info("Creating frame analyzer")
    qr_scanner = QRScanner()
    face_detector = NullFaceDetector()
    return FrameAnalyzer(qr_scanner=qr_scanner, face_detector=face_detector)


def create_clock(*, frame_rate):
    logging.info(f'Creating clock with rate {frame_rate}')
    return Clock(frame_rate)


def create_sound_player(*, theme, quiet):
    logging.info(f'Creating sound player with theme {theme}, quiet={quiet}')
    return SoundPlayer(theme, quiet)


def create_frame_viewer(surface, frame_size):
    window_width, window_height = surface.get_size()
    frame_width, frame_height = frame_size
    x = (window_width - frame_width) // 2
    y = 0
    return FrameViewer(surface, (x, y))


def screen_size():
    info = pygame.display.Info()
    return (info.current_w, info.current_h)