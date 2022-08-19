import logging
from time import sleep, monotonic
from attendances.analyzer import FrameAnalyzer
from attendances.tools.capturers import DummyCapturer, VideoCapturer
from attendances.gui import _create_frame_analyzer
from attendances.gui.clock import Clock
from attendances.model.model import Model
from attendances.tools.sound import SoundPlayer
import time


def now():
    return monotonic()


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


def _create_clock(settings):
    rate = settings['frame-rate']
    logging.info(f'Creating clock with rate {rate}')
    return Clock(rate)


def _create_model(settings, clock):
    video_capturer = _create_capturer(settings.subtree('video-capturing'))
    frame_analyzer = _create_frame_analyzer(settings.subtree('frame-analyzing'))
    names = [str(k).rjust(5, '0') for k in range(0, 98)]
    return Model(
        settings=settings,
        video_capturer=video_capturer,
        frame_analyzer=frame_analyzer,
        clock=clock,
        names=names
    )


def _create_sound_player(settings):
    logging.info('Creating sound player')
    return SoundPlayer(settings['theme'], quiet=settings['quiet'])


def run(settings):
    logging.info('Initializing...')
    sound_player = _create_sound_player(settings.subtree('sound'))
    clock = _create_clock(settings)
    model = _create_model(settings, clock)

    for person in model.attendances.people:
        person.present.add_observer(sound_player.success)

    logging.info('Ready and keeping an eye on you...')

    with model:
        clock.update()
        time.sleep(50)
