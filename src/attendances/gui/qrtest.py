import logging
import pygame
import json
from attendances.cells import Cell
from attendances.gui.grid import Grid
from attendances.gui.highlight import Highlighter
from attendances.gui.factories import create_frame_viewer, create_window
from attendances.server import Channel, server
from attendances.pipeline import *
from functools import partial
import attendances.commands as commands
from attendances.gui.fps import FpsViewer
import attendances.gui.factories as factories
from attendances.settings import settings
from attendances.tools.capturing import InjectingCapturer


def _create_clock():
    return factories.create_clock(frame_rate=settings.frame_rate)


def _create_window():
    width, height = settings.window_size
    return factories.create_window(width, height)


def _create_frame_analyzer():
    return factories.create_frame_analyzer()


def _create_capturer():
    # capturer = factories.create_dummy_capturer()
    capturer = factories.create_camera_capturer(*settings.frame_size)
    return InjectingCapturer(capturer)


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
    return counter.derive(lambda n: f'{transformer} : {n}')


def _create_transformation_chain(*, source_node, transformation, frame_analyzer, surface, rect, clock, font):
    analyzer = AnalyzerNode([transformation], frame_analyzer)
    counter = Cell(0)
    label = _create_label(counter, transformation)
    highlighter = Highlighter(surface=surface, rectangle=rect, label=label, font=font)

    source_node.link(analyzer.analyze)
    analyzer.link(partial(_log_qr_detection, transformation))
    analyzer.link(_ignore_parameters(highlighter.highlight))
    analyzer.link(_ignore_parameters(_incrementer(counter)))
    clock.on_tick(highlighter.tick)
    clock.on_tick(analyzer.tick)

    highlighter.render()


def test_qr():
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

    show_framerate = settings.show_fps
    frame_size = settings.frame_size
    analyze_every_n_frames = settings.analyze_every_n_frames
    font_size = 32

    channel = Channel()
    font = pygame.font.SysFont(None, font_size)
    clock = _create_clock()
    surface = _create_window()
    capturing_surface = pygame.Surface(frame_size)
    video_capturer = _create_capturer()
    frame_analyzer = _create_frame_analyzer()
    context = commands.Context(attendances=None, capturer=video_capturer)
    frame_viewer = create_frame_viewer(surface, frame_size)
    fps = Cell(0)

    if show_framerate:
        FpsViewer(surface, fps)

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, capturing_surface)
        skipper_node = SkipperNode(analyze_every_n_frames)
        wrapper_node = ImageWrapper()
        capturing_node.link(skipper_node.perform)
        skipper_node.link(wrapper_node.wrap)

        transformations = [
            'original',
            'grayscale',
            'bw',
            'bw_mean',
            'bw_gaussian'
        ]
        grid = create_grid()

        for index, transformation in enumerate(transformations):
            rect = grid.child_rectangle((index, 0))

            _create_transformation_chain(
                source_node=wrapper_node,
                transformation=transformation,
                frame_analyzer=frame_analyzer,
                surface=surface,
                rect=rect,
                clock=clock,
                font=font
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
                    response = command_object.execute(context)
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
