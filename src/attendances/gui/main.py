import logging
import pygame
import json
from pathlib import Path
from functools import partial
from attendances.cells import Cell
from attendances.gui.attviewer import AttendancesViewer
import attendances.gui.factories as factories
from attendances.gui.fps import FpsViewer
from attendances.model.attendances import Attendances
from attendances.server import Channel, server
from attendances.pipeline import *
import attendances.commands as commands
from attendances.gui.highlight import Highlighter
from attendances.registration import FileRegistration
from attendances.data import load_data
import attendances.settings as settings


def _create_sound_player():
    return factories.create_sound_player(theme=settings.sound_theme, quiet=settings.quiet)


def _create_clock():
    return factories.create_clock(frame_rate=settings.frame_rate)


def _create_window():
    width, height = settings.window_size
    return factories.create_window(width, height)


def _create_frame_analyzer():
    return factories.create_frame_analyzer()


def _create_capturer():
    # return create_dummy_capturer()
    return factories.create_camera_capturer(640, 480)


def _list_qr_transformations():
    return settings.qr_transformations

def create_registration_viewer(*, rectangle, clock, surface, attendances):
    def create_single_registration_viewer():
        def observe_person(person):
            def update_label():
                label.value = person.name
            person.present.on_value_changed(update_label)

        label = Cell('')
        font = pygame.font.SysFont(None, 64)
        highlighter = Highlighter(surface=surface, rectangle=rectangle, label=label, font=font)
        highlighter.render()
        clock.on_tick(highlighter.tick)
        for person in attendances.people:
            observe_person(person)

    def create_overview_registration_viewer():
        ncolumns = 24
        font_size = 16
        font = pygame.font.SysFont(None, font_size)
        viewer = AttendancesViewer(surface=surface, attendances=attendances, rectangle=rectangle, ncolumns=ncolumns, font=font)
        viewer.render()
        clock.on_tick(viewer.tick)

    # create_single_registration_viewer()
    create_overview_registration_viewer()


def run():
    def compute_registration_viewer_rectangle():
        return pygame.Rect(
            0,
            frame_height,
            window_width,
            window_height-frame_height
        )

    def create_registrations():
        registration = FileRegistration(attendances_file)
        for person in attendances.people:
            person.present.on_value_changed(partial(registration.register, person))


    pygame.init()

    show_framerate = settings.show_fps
    frame_width, frame_height = frame_size = settings.frame_size
    analyze_every_n_frames = settings.analyze_every_n_frames
    attendances_file = Path(settings.registration_file)

    channel = Channel()
    clock = _create_clock()
    surface = _create_window()
    window_width, window_height = surface.get_size()
    capturing_surface = pygame.Surface(frame_size)
    sound_player = _create_sound_player()
    video_capturer = _create_capturer()
    frame_analyzer = _create_frame_analyzer()
    names = load_data()
    attendances = Attendances(names)
    create_registrations()
    create_registration_viewer(
        rectangle=compute_registration_viewer_rectangle(),
        clock=clock,
        surface=surface,
        attendances=attendances
    )
    context = commands.Context(attendances=attendances, capturer=video_capturer)
    fps = Cell(0)

    for person in attendances.people:
        person.present.on_value_changed(sound_player.success)

    frame_viewer = factories.create_frame_viewer(surface, frame_size)

    if show_framerate:
        FpsViewer(surface, fps)

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, capturing_surface)
        skipper_node = SkipperNode(analyze_every_n_frames)
        wrapping_node = ImageWrapper()
        analyzing_node = AnalyzerNode(_list_qr_transformations(), frame_analyzer)
        registering_node = RegisteringNode(attendances)

        capturing_node.link(skipper_node.perform)
        capturing_node.link(frame_viewer.new_frame)
        skipper_node.link(wrapping_node.wrap)
        wrapping_node.link(analyzing_node.analyze)
        analyzing_node.link(registering_node.update_attendances)
        analyzing_node.link(frame_viewer.new_analysis)

        clock.on_tick(frame_viewer.tick)
        clock.on_tick(lambda _: capturing_node.capture())
        clock.on_tick(analyzing_node.tick)

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
