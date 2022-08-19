import logging
import pygame
import json
from attendances.gui.attviewer import AttendancesViewer
from attendances.server import Channel, server
from attendances.sound import SoundPlayer
from attendances.tools.capturers import DummyCapturer, VideoCapturer
from attendances.gui.viewer import FrameViewer
from attendances.gui.clock import Clock
from attendances.model import Model
from attendances.analyzer import FrameAnalyzer
import attendances.commands as commands


def _create_capturer(settings):
    if settings['dummy']:
        logging.info('Creating dummy capturer')
        return DummyCapturer()
    else:
        size = (settings['width'], settings['height'])
        logging.info(f'Creating video capturer with size {size}')
        return VideoCapturer.default_camera(size)


def _create_frame_analyzer(settings):
    logging.info("Creating frame analyzer")
    return FrameAnalyzer()


def _get_window_size(settings):
    info = pygame.display.Info()
    window_width, window_height = settings['width'], settings['height']
    if window_width == 0:
        window_width = info.current_w
    if window_height == 0:
        window_height = info.current_h
    return window_width, window_height


def _create_clock(settings):
    rate = settings['frame-rate']
    logging.info(f'Creating clock with rate {rate}')
    return Clock(rate)


def _create_window(settings):
    width, height = _get_window_size(settings)
    logging.info(f'Creating window with size {width}x{height}')
    return pygame.display.set_mode((width, height))


def _create_sound_player(settings):
    logging.info('Creating sound player')
    return SoundPlayer(settings['theme'], quiet=settings['quiet'])


def _create_frame_viewer(model, window_size):
    window_width, window_height = window_size
    frame_width, frame_height = model.current_frame.value.get_size()
    x = (window_width - frame_width) // 2
    y = 0
    return FrameViewer(model, (x, y))


def _create_attendances_viewer(settings, model, window_size):
    window_width, window_height = window_size
    rect = pygame.Rect(0, 480, window_width, window_height - 480)
    return AttendancesViewer(settings, model, rect)


def run(settings):
    def create_model():
        names = [str(k).rjust(5, '0') for k in range(0, 98)]
        return Model(
            settings=settings,
            video_capturer=video_capturer,
            frame_analyzer=frame_analyzer,
            names=names
        )

    pygame.init()

    channel = Channel()
    clock = _create_clock(settings)
    surface = _create_window(settings.subtree('gui.window'))
    sound_player = _create_sound_player(settings.subtree('sound'))
    video_capturer = _create_capturer(settings.subtree('video-capturing'))
    frame_analyzer = _create_frame_analyzer(settings.subtree('frame-analyzing'))
    model = create_model()

    for person in model.attendances.people:
        person.present.add_observer(sound_player.success)

    frame_viewer = _create_frame_viewer(model, surface.get_size())
    attendances_viewer = _create_attendances_viewer(settings.subtree('gui.attendances'), model, surface.get_size())

    with server(channel), model:
        clock.add_observer(frame_viewer.tick)
        clock.add_observer(attendances_viewer.tick)
        clock.add_observer(model.tick)

        active = True
        while active:
            if channel.message_from_server_waiting:
                request = json.loads(channel.receive_from_server())
                try:
                    logging.debug(f'Received {request}')
                    command_class = commands.find_command_with_name(request['command'])
                    command_object = command_class(**request['args'])
                    response = command_object.execute(model, settings)
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
