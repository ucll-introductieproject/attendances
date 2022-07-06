from time import sleep, monotonic
from absentees.capturer import Capturer
import chime
import pygame
from absentees.cells import Cell
from pyzbar.pyzbar import decode


def now():
    return monotonic()


def run(settings, sound_player):
    capture_rate = settings['capture.rate']
    capture_width = settings['capture.width']
    capture_height = settings['capture.height']
    ignore_repetition_duration = settings['qr.ignore-repetition-duration']

    def initialize():
        print('Initializing...')
        chime.theme(settings['sound.theme'])
        pygame.init()
        pygame.camera.init()

    def scan():
        scanned = {}

        camera = Capturer.default_camera()
        capture_surface = Cell(pygame.Surface((capture_width, capture_height)))
        capture_ndarray = capture_surface.derive(lambda x: pygame.surfarray.array3d(x).swapaxes(0, 1))

        with Capturer(camera, capture_surface) as capture:
            print('Ready to scan QR codes!')
            while True:
                capture()
                for decoded in decode(capture_ndarray.value):
                    data = decoded.data.decode('utf-8')
                    if data not in scanned:
                        scanned[data] = now()
                        print(data)
                        sound_player.success()
                    else:
                        delta = now() - scanned[data]
                        if delta > ignore_repetition_duration / 1000:
                            print(f'Already scanned {data}')

                sleep(1 / capture_rate)

    initialize()
    scan()