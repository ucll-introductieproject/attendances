import logging
import pygame
import json
from attendances.cells import Cell
from attendances.gui.attviewer import AttendancesViewer
from attendances.gui.highlight import Highlighter
from attendances.imaging import identity, to_black_and_white, to_black_and_white_gaussian, to_black_and_white_mean, to_grayscale
from attendances.model.attendances import Attendances
from attendances.pipeline.transforming import TransformerNode
from attendances.server import Channel, server
from attendances.tools.sound import SoundPlayer
from attendances.tools.capturing import DummyCapturer, VideoCapturer
from attendances.gui.viewer import FrameViewer
from attendances.gui.clock import Clock
from attendances.pipeline import *
from attendances.tools.analyzing import FrameAnalyzer
from functools import partial
import attendances.commands as commands


def _create_capturer(settings):
    if settings['dummy']:
        logging.info('Creating dummy capturer')
        return DummyCapturer()
    else:
        size = (settings['width'], settings['height'])
        logging.info(f'Creating video capturer with size {size}')
        return VideoCapturer.default_camera(size)


def _create_frame_analyzer(surface):
    logging.info("Creating frame analyzer")
    return FrameAnalyzer(highlight_qr=True)


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


def _create_frame_viewer(surface, frame_size):
    window_width, window_height = surface.get_size()
    frame_width, frame_height = frame_size
    x = (window_width - frame_width) // 2
    y = 0
    return FrameViewer(surface, (x, y))


def _create_attendances_viewer(settings, model, window_size):
    window_width, window_height = window_size
    rect = pygame.Rect(0, 480, window_width, window_height - 480)
    return AttendancesViewer(settings, model, rect)


def run(settings):
    pygame.init()

    channel = Channel()
    frame_size = (settings['video-capturing.width'], settings['video-capturing.height'])
    clock = _create_clock(settings)
    surface = _create_window(settings.subtree('gui.window'))
    capturing_surface = pygame.Surface(frame_size)
    sound_player = _create_sound_player(settings.subtree('sound'))
    video_capturer = _create_capturer(settings.subtree('video-capturing'))
    frame_analyzer = _create_frame_analyzer(settings.subtree('frame-analyzing'))
    names = [str(k).rjust(5, '0') for k in range(0, 98)]
    attendances = Attendances(names)
    context = commands.Context(attendances=attendances, capturer=video_capturer)

    for person in attendances.people:
        person.present.add_observer(sound_player.success)

    frame_viewer = FrameViewer(surface, (0, 0))
    # attendances_viewer = _create_attendances_viewer(settings.subtree('gui.attendances'), model, surface.get_size())

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, capturing_surface)
        analyzing_node = AnalyzerNode(frame_analyzer)
        registering_node = RegisteringNode(attendances)

        capturing_node.on_captured(analyzing_node.analyze)
        capturing_node.on_captured(frame_viewer.new_frame)
        analyzing_node.on_analysis(registering_node.update_attendances)
        analyzing_node.on_analysis(frame_viewer.new_analysis)

        # clock.on_tick(attendances_viewer.tick)
        clock.on_tick(frame_viewer.tick)
        clock.on_tick(lambda _: capturing_node.capture())

        active = True
        while active:
            if channel.message_from_server_waiting:
                request = json.loads(channel.receive_from_server())
                try:
                    logging.debug(f'Received {request}')
                    command_class = commands.find_command_with_name(request['command'])
                    command_object = command_class(**request['args'])
                    response = command_object.execute(context, settings)
                    channel.respond_to_server(response)
                except:
                    channel.respond_to_server('exception thrown')
                    raise

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False

            clock.update()

            pygame.display.flip()



def test_qr(settings):
    def show_qr(description, analysis):
        for qr_code in analysis.qr_codes:
            logging.info(f'{description} found {qr_code.data}')

    def highlighter_rect(i):
        width = 200
        height = 50
        left = i * width
        top = 800
        return pygame.Rect(left, top, width, height)

    def ignore_parameters(func):
        return lambda *_: func()

    pygame.init()

    frame_size = (settings['video-capturing.width'], settings['video-capturing.height'])
    channel = Channel()
    clock = _create_clock(settings)
    surface = _create_window(settings.subtree('gui.window'))
    capturing_surface = pygame.Surface(frame_size)
    video_capturer = _create_capturer(settings.subtree('video-capturing'))
    frame_analyzer = _create_frame_analyzer(settings.subtree('frame-analyzing'))
    context = commands.Context(attendances=None, capturer=video_capturer)
    frame_viewer = _create_frame_viewer(surface, frame_size)

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, capturing_surface)

        transformers = [identity, to_grayscale, to_black_and_white, to_black_and_white_mean, to_black_and_white_gaussian]
        transformer_nodes = [TransformerNode(f) for f in transformers]
        analyzer_nodes = [AnalyzerNode(frame_analyzer) for _ in transformers]
        labels = [Cell(transformer.__name__) for transformer in transformers]
        highlighters = [Highlighter(surface, highlighter_rect(i), label) for i, label in enumerate(labels)]

        for transformer, transformer_node, analyzer_node, highlighter in zip(transformers, transformer_nodes, analyzer_nodes, highlighters):
            capturing_node.on_captured(transformer_node.transform)
            transformer_node.on_transformed(analyzer_node.analyze)
            analyzer_node.on_analysis(partial(show_qr, transformer.__name__))
            analyzer_node.on_analysis(ignore_parameters(highlighter.highlight))

        capturing_node.on_captured(frame_viewer.new_frame)

        for highlighter in highlighters:
            highlighter.render()

        for observer in [ frame_viewer.tick,
                          ignore_parameters(capturing_node.capture),
                          *(highlighter.tick for highlighter in highlighters)
                          ]:
            clock.on_tick(observer)


        active = True
        while active:
            if channel.message_from_server_waiting:
                request = json.loads(channel.receive_from_server())
                try:
                    logging.debug(f'Received {request}')
                    command_class = commands.find_command_with_name(request['command'])
                    command_object = command_class(**request['args'])
                    response = command_object.execute(context, settings)
                    channel.respond_to_server(response)
                except:
                    channel.respond_to_server('exception thrown')
                    raise

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False

            clock.update()

            pygame.display.flip()
