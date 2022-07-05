from time import sleep, monotonic
from absentees.capturer import Capturer
import chime
import pygame
from absentees.cells import Cell
from pyzbar.pyzbar import decode


def now():
    return monotonic()


def run(theme, source, quiet, wait, ignore):
    def initialize():
        print('Initializing...')
        chime.theme(theme)
        pygame.init()
        pygame.camera.init()

    def play_success_sound():
        if not quiet:
            chime.success()

    def scan():
        scanned = {}

        camera = Capturer.default_camera()
        capture_width, capture_height = 640, 480
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
                        play_success_sound()
                    else:
                        delta = now() - scanned[data]
                        if delta > ignore / 1000:
                            print(f'Already scanned {data}')

                sleep(wait / 1000)

    initialize()
    scan()