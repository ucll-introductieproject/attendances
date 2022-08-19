import logging
import pygame
from attendances.server import Channel, server
from attendances.model.attendances import Attendances
from attendances.tools.analyzing import FrameAnalyzer
from attendances.tools.capturing import DummyCapturer, VideoCapturer
from attendances.gui import _create_frame_analyzer
from attendances.tools.sound import SoundPlayer
from attendances.pipeline import *
import time
import json
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


def _create_sound_player(settings):
    logging.info('Creating sound player')
    return SoundPlayer(settings['theme'], quiet=settings['quiet'])


def run(settings):
    def show_analysis_results(results):
        print(results)

    surface_size = (settings['video-capturing.width'], settings['video-capturing.height'])
    surface = pygame.Surface(surface_size)
    sound_player = _create_sound_player(settings.subtree('sound'))
    video_capturer = _create_capturer(settings.subtree('video-capturing'))
    frame_analyzer = _create_frame_analyzer(settings.subtree('frame-analyzing'))
    names = [str(k).rjust(5, '0') for k in range(0, 98)]
    attendances = Attendances(names)
    channel = Channel()
    context = commands.Context(attendances=attendances, capturer=video_capturer)

    for person in attendances.people:
        person.present.add_observer(sound_player.success)

    logging.info('Ready and keeping an eye on you...')

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, surface)
        analyzing_node = AnalyzerNode(frame_analyzer)
        registering_node = RegisteringNode(attendances)

        capturing_node.on_captured(analyzing_node.analyze)
        analyzing_node.on_analysis(registering_node.update_attendances)
        analyzing_node.on_analysis(show_analysis_results)

        while True:
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

            capturing_node.capture()
            time.sleep(0.2)
