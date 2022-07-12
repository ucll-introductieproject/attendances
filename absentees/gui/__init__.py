import logging
import pygame
import json
from absentees.gui.attviewer import AttendancesViewer
from absentees.server import Channel, server
from absentees.sound import SoundPlayer
from absentees.countdown import Countdown
from absentees.cells import Cell
from absentees.capturer import DummyCapturer, VideoCapturer
from absentees.gui.viewer import FrameViewer
from absentees.gui.clock import Clock
from absentees.repeater import Repeater
from absentees.analyzer import FrameAnalyzer
import absentees.commands as commands
from contextlib import contextmanager



def create_capturer(settings):
    if settings['capture.dummy']:
        return DummyCapturer
    else:
        camera_name = VideoCapturer.default_camera()
        return lambda target: VideoCapturer(camera_name, target)


@contextmanager
def auto_capture(settings, surface_cell):
    rate = settings['capture.rate']
    capturer = create_capturer(settings)
    with capturer(surface_cell.value) as capture:
        def capture_and_refresh():
            capture()
            surface_cell.refresh()

        repeater = Repeater(capture_and_refresh, 1 / rate)
        yield repeater


class Person:
    def __init__(self, name):
        assert isinstance(name, str)
        self.__name = name
        self.__present = False

    @property
    def name(self):
        return self.__name

    @property
    def present(self):
        return self.__present

    @present.setter
    def present(self, value):
        self.__present = value


class Attendances:
    def __init__(self, names):
        self.__people = {name: Person(name) for name in names}

    @property
    def names(self):
        return self.__people.keys()

    @property
    def people(self):
        return self.__people.values()

    def register(self, name):
        self.__people[name].present = True


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


def create_attendances_viewer(settings, model, window_size):
    window_width, window_height = window_size
    rect = pygame.Rect(0, 480, window_width, window_height - 480)
    return AttendancesViewer(settings, model, rect)


def run(settings, quiet):
    pygame.init()

    channel = Channel()
    clock = create_clock(settings)
    window_size = get_window_size(settings)
    surface = create_window(window_size)
    sound_player = create_sound_player(settings, quiet)

    model = Model(settings, [str(k).rjust(5, '0') for k in range(0, 98)])
    frame_viewer = create_frame_viewer(model, window_size)
    attendances_viewer = create_attendances_viewer(settings, model, window_size)
    analysis_repeater = Repeater(model.analyze_current_frame, settings['qr.capture-rate'])

    with server(channel), auto_capture(settings, model.current_frame) as auto_capturer:
        clock.add_observer(auto_capturer.tick)
        clock.add_observer(frame_viewer.tick)
        clock.add_observer(analysis_repeater.tick)

        active = True
        while active:
            if channel.message_from_server_waiting:
                request = json.loads(channel.receive_from_server())
                try:
                    logging.debug(f'Received {request}')
                    command_class = commands.find_command_with_name(request['command'])
                    command_object = command_class(**request['args'])
                    response = command_object.execute(model)
                    channel.respond_to_server(response)
                except:
                    channel.respond_to_server('exception thrown')
                    raise

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False

            clock.update()

            frame_viewer.render(surface)
            attendances_viewer.render(surface)
            pygame.display.flip()
