import logging
import pygame
import json
from attendances.cells import Cell
from attendances.gui.grid import Grid
from attendances.gui.highlight import Highlighter
from attendances.imaging.transformations import identity, to_black_and_white, to_black_and_white_gaussian, to_black_and_white_mean, to_grayscale
from attendances.pipeline.transforming import TransformerNode
from attendances.server import Channel, server
from attendances.pipeline import *
from functools import partial
import attendances.commands as commands
from attendances.gui.factories import create_capturer, create_clock, create_frame_analyzer, create_frame_viewer, create_sound_player, create_window
from attendances.gui.fps import FpsViewer


def _log_qr_detection(transformer_name, analysis):
    for qr_code in analysis.qr_codes:
        logging.info(f'{transformer_name} found {qr_code.data}')


def _incrementer(counter):
    def increment():
        counter.value += 1
    return increment


def _ignore_parameters(func):
    return lambda *_: func()


def _create_label(counter, transformer):
    return counter.derive(lambda n: f'{transformer.__name__} : {n}')


def _create_transformation_chain(*, capturing_node, transformation, frame_analyzer, surface, rect, clock):
    analyzer = AnalyzerNode([transformation], frame_analyzer)
    counter = Cell(0)
    label = _create_label(counter, transformation)
    highlighter = Highlighter(surface, rect, label)

    capturing_node.link(analyzer.analyze)
    analyzer.link(partial(_log_qr_detection, transformation.__name__))
    analyzer.link(_ignore_parameters(highlighter.highlight))
    analyzer.link(_ignore_parameters(_incrementer(counter)))
    clock.on_tick(highlighter.tick)

    highlighter.render()


def test_qr(settings):
    def determine_grid_rect():
        frame_width, frame_height = frame_size
        window_width, window_height = surface.get_size()
        width = window_width
        height = 20
        top = frame_height + (window_height - frame_height) / 2 - height / 2
        left = 0
        return pygame.Rect(left, top, width, height)

    def create_grid():
        rect = determine_grid_rect()
        size = (len(transformations), 1)
        return Grid(rect, size)

    pygame.init()
    frame_size = (settings['video-capturing.width'], settings['video-capturing.height'])
    channel = Channel()
    clock = create_clock(settings.subtree('qrtest'))
    surface = create_window(settings.subtree('gui.window'))
    capturing_surface = pygame.Surface(frame_size)
    video_capturer = create_capturer(settings.subtree('video-capturing'))
    frame_analyzer = create_frame_analyzer(highlight_qr=False)
    context = commands.Context(attendances=None, capturer=video_capturer)
    frame_viewer = create_frame_viewer(surface, frame_size)
    fps = Cell(0)

    if settings['gui.show-fps']:
        FpsViewer(surface, fps)

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, capturing_surface)

        transformations = [identity, to_grayscale, to_black_and_white, to_black_and_white_mean, to_black_and_white_gaussian]
        grid = create_grid()

        for index, transformation in enumerate(transformations):
            rect = grid.child_rectangle((index, 0))

            _create_transformation_chain(
                capturing_node=capturing_node,
                transformation=transformation,
                frame_analyzer=frame_analyzer,
                surface=surface,
                rect=rect,
                clock=clock
            )

        capturing_node.link(frame_viewer.new_frame)

        clock.on_tick(frame_viewer.tick)
        clock.on_tick(_ignore_parameters(capturing_node.capture))

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
            fps.value = clock.fps

            pygame.display.flip()
