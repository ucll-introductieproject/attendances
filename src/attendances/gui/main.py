import logging
import pygame
import json
from attendances.cells import Cell
from attendances.gui.factories import create_capturer, create_clock, create_frame_analyzer, create_frame_viewer, create_sound_player, create_window
from attendances.gui.fps import FpsViewer
from attendances.imaging.transformations import get_transformation_by_id
from attendances.model.attendances import Attendances
from attendances.server import Channel, server
from attendances.pipeline import *
import attendances.commands as commands


def run(settings):
    pygame.init()

    channel = Channel()
    frame_size = (settings['video-capturing.width'], settings['video-capturing.height'])
    clock = create_clock(settings.subtree('gui'))
    surface = create_window(settings.subtree('gui.window'))
    capturing_surface = pygame.Surface(frame_size)
    sound_player = create_sound_player(settings.subtree('sound'))
    video_capturer = create_capturer(settings.subtree('video-capturing'))
    frame_analyzer = create_frame_analyzer(highlight_qr=True)
    names = [str(k).rjust(5, '0') for k in range(0, 98)]
    attendances = Attendances(names)
    context = commands.Context(attendances=attendances, capturer=video_capturer)
    fps = Cell(0)

    for person in attendances.people:
        person.present.on_value_changed(sound_player.success)

    frame_viewer = create_frame_viewer(surface, frame_size)
    # attendances_viewer = _create_attendances_viewer(settings.subtree('gui.attendances'), model, surface.get_size())

    if settings['gui.show-fps']:
        FpsViewer(surface, fps)

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, capturing_surface)
        skipper_node = SkipperNode(settings['gui.skip-rate'])
        wrapping_node = ImageWrapper()
        analyzing_node = AnalyzerNode(settings['qr.transformations'], frame_analyzer)
        registering_node = RegisteringNode(attendances)

        capturing_node.link(skipper_node.perform)
        skipper_node.link(wrapping_node.wrap)
        wrapping_node.link(analyzing_node.analyze)
        wrapping_node.link(frame_viewer.new_frame)
        analyzing_node.link(registering_node.update_attendances)
        analyzing_node.link(frame_viewer.new_analysis)

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
            fps.value = clock.fps

            pygame.display.flip()
