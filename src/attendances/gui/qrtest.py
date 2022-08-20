import logging
import pygame
import json
from attendances.cells import Cell
from attendances.gui.highlight import Highlighter
from attendances.imaging import identity, to_black_and_white, to_black_and_white_gaussian, to_black_and_white_mean, to_grayscale
from attendances.pipeline.transforming import TransformerNode
from attendances.server import Channel, server
from attendances.pipeline import *
from functools import partial
import attendances.commands as commands
from attendances.gui.factories import create_capturer, create_clock, create_frame_analyzer, create_frame_viewer, create_sound_player, create_window


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
    transformer = TransformerNode(transformation)
    analyzer = AnalyzerNode(frame_analyzer)
    counter = Cell(0)
    label = _create_label(counter, transformation)
    highlighter = Highlighter(surface, rect, label)

    capturing_node.on_captured(transformer.transform)
    transformer.on_transformed(analyzer.analyze)
    analyzer.on_analysis(partial(_log_qr_detection, transformation.__name__))
    analyzer.on_analysis(_ignore_parameters(highlighter.highlight))
    analyzer.on_analysis(_ignore_parameters(_incrementer(counter)))
    clock.on_tick(highlighter.tick)

    highlighter.render()


def test_qr(settings):
    def highlighter_rect(i):
        width = 200
        height = 50
        left = i * width
        top = 800
        return pygame.Rect(left, top, width, height)

    pygame.init()
    frame_size = (settings['video-capturing.width'], settings['video-capturing.height'])
    channel = Channel()
    clock = create_clock(settings)
    surface = create_window(settings.subtree('gui.window'))
    capturing_surface = pygame.Surface(frame_size)
    video_capturer = create_capturer(settings.subtree('video-capturing'))
    frame_analyzer = create_frame_analyzer(settings.subtree('frame-analyzing'))
    context = commands.Context(attendances=None, capturer=video_capturer)
    frame_viewer = create_frame_viewer(surface, frame_size)

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, capturing_surface)

        transformations = [identity, to_grayscale, to_black_and_white, to_black_and_white_mean, to_black_and_white_gaussian]

        for index, transformation in enumerate(transformations):
            rect = highlighter_rect(index)

            _create_transformation_chain(
                capturing_node=capturing_node,
                transformation=transformation,
                frame_analyzer=frame_analyzer,
                surface=surface,
                rect=rect,
                clock=clock
            )

        capturing_node.on_captured(frame_viewer.new_frame)

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

            pygame.display.flip()
