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

    def incrementer(counter):
        def increment():
            counter.value += 1
        return increment

    def create_label(counter, transformer):
        return counter.derive(lambda n: f'{transformer.__name__} : {n}')

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

        transformers = [identity, to_grayscale, to_black_and_white, to_black_and_white_mean, to_black_and_white_gaussian]
        transformer_nodes = [TransformerNode(f) for f in transformers]
        analyzer_nodes = [AnalyzerNode(frame_analyzer) for _ in transformers]
        detection_counters = [Cell(0) for _ in transformers]
        labels = [create_label(counter, transformer) for counter, transformer in zip(detection_counters, transformers)]
        highlighters = [Highlighter(surface, highlighter_rect(i), label) for i, label in enumerate(labels)]

        for transformer, transformer_node, analyzer_node, highlighter, counter in zip(transformers, transformer_nodes, analyzer_nodes, highlighters, detection_counters):
            capturing_node.on_captured(transformer_node.transform)
            transformer_node.on_transformed(analyzer_node.analyze)
            analyzer_node.on_analysis(partial(show_qr, transformer.__name__))
            analyzer_node.on_analysis(ignore_parameters(highlighter.highlight))
            analyzer_node.on_analysis(ignore_parameters(incrementer(counter)))

        capturing_node.on_captured(frame_viewer.new_frame)

        for highlighter in highlighters:
            highlighter.render()

        for observer in [frame_viewer.tick,
                         ignore_parameters(capturing_node.capture),
                         *(highlighter.tick for highlighter in highlighters)]:
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
