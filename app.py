import cv2
from pyzbar.pyzbar import decode
from contextlib import contextmanager
from time import sleep, monotonic
import pygame
import click
import chime
import pygame
import pygame.camera


def now():
    return monotonic()


@contextmanager
def video_capture(source):
    def read_frame():
        _, frame = vc.read()
        return frame
    try:
        vc = cv2.VideoCapture(source)
        yield read_frame
    finally:
        vc.release()


@click.group()
def cli():
    pass


@click.command()
@click.option('--theme', help=f"One of {', '.join(chime.themes())}", default='big-sur')
@click.option('--source', help='Index of video source', default=0, type=int)
@click.option('--quiet', is_flag=True, help='No sound')
@click.option('--wait', help='Milliseconds between polls', default=500, type=int)
@click.option('--ignore', help='Milliseconds during which to ignore repeat scans', default=1000, type=int)
def tui(theme, source, quiet, wait, ignore):
    def initialize():
        print('Initializing...')
        chime.theme(theme)

    def play_success_sound():
        if not quiet:
            chime.success()

    def scan():
        scanned = {}

        with video_capture(source) as read_frame:
            print('Ready to scan QR codes!')
            while True:
                for decoded in decode(read_frame()):
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


@cli.command()
def gui():
    pygame.init()
    pygame.camera.init()
    info = pygame.display.Info()
    window_width, window_height = info.current_w, info.current_h
    capture_width, capture_height = 640, 480
    surface = pygame.display.set_mode((window_width, window_height))
    capture_surface = pygame.Surface((capture_width, capture_height))
    camera = pygame.camera.Camera(pygame.camera.list_cameras()[0], (capture_width, capture_height), 'RGB')
    camera.start()
    try:
        active = True
        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False

            camera.get_image(capture_surface)
            surface.blit(capture_surface, (0, 0))
            pygame.display.flip()
    finally:
        camera.stop()
        pass



cli.add_command(tui)
cli.add_command(gui)

if __name__ == '__main__':
    cli()
