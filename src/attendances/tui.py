import logging
from pathlib import Path
import pygame
from functools import partial
from attendances.registration import FileRegistration
from attendances.server import Channel, server
from attendances.model.attendances import Attendances
from attendances.pipeline import *
import attendances.commands as commands
import attendances.gui.factories as factories
from attendances.data import load_data
from attendances.settings import settings
import time
import json

from attendances.tools.capturing import InjectingCapturer


def _create_sound_player():
    return factories.create_sound_player(theme='big-sur', quiet=False)


def _create_capturer():
    return factories.create_camera_capturer(*settings.frame_size)

def _create_capturer():
    # capturer = create_dummy_capturer()
    capturer = factories.create_camera_capturer(640, 480)
    return InjectingCapturer(capturer)


def _create_frame_analyzer():
    return factories.create_frame_analyzer()


def _create_qr_transformations():
    return [
        # 'original',
        # 'grayscale',
        # 'bw',
        'bw_mean',
        # 'bw_gaussian',
    ]


def run():
    def create_registrations():
        logging.info(f'Appending registrations to {attendances_file}')
        registration = FileRegistration(attendances_file)
        for person in attendances.people:
            person.present.on_value_changed(partial(registration.register, person))

    def show_analysis_results(results):
        print(results)

    attendances_file = Path(settings.registration_file)
    surface = pygame.Surface(settings.frame_size)
    sound_player = _create_sound_player()
    video_capturer = _create_capturer()
    frame_analyzer = _create_frame_analyzer()
    pause_duration = 0.2
    attendances = Attendances(load_data())
    channel = Channel()
    create_registrations()
    context = commands.Context(attendances=attendances, capturer=video_capturer)

    for person in attendances.people:
        person.present.on_value_changed(sound_player.success)

    logging.info('Ready and keeping an eye on you...')

    with server(channel), video_capturer as handle:
        capturing_node = CapturingNode(handle, surface)
        wrapper_node = ImageWrapper()
        analyzing_node = AnalyzerNode(_create_qr_transformations(), frame_analyzer)
        registering_node = RegisteringNode(attendances)

        capturing_node.link(wrapper_node.wrap)
        wrapper_node.link(analyzing_node.analyze)
        analyzing_node.link(registering_node.update_attendances)
        analyzing_node.link(show_analysis_results)

        while True:
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

            capturing_node.capture()
            time.sleep(pause_duration)
            analyzing_node.tick(pause_duration)
