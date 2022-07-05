import cv2
from pyzbar.pyzbar import decode
from contextlib import contextmanager
from time import sleep, monotonic
import pygame
import click
import chime
import pygame
import pygame.camera
from absentees.countdown import Countdown
from absentees.cells import Cell
from absentees.settings import load_settings
from pathlib import Path
import json


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


class Capturer:
    def __init__(self, camera, target_surface):
        width, height = target_surface.value.get_size()
        self.__camera = pygame.camera.Camera(camera, (width, height), 'RGB')
        self.__target = target_surface

    def __enter__(self):
        def capture():
            self.__camera.get_image(self.__target.value)
            self.__target.refresh()
        self.__camera.start()
        return capture

    def __exit__(self, exception, value, traceback):
        self.__camera.stop()


@click.command()
def gui():
    settings = load_settings(Path.home().joinpath('absentees.config.json'))
    fps = settings['frame_rate']
    capture_fps = settings['capture_rate']
    pygame.init()
    pygame.camera.init()
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    font = pygame.font.SysFont(None, 48)
    camera = pygame.camera.list_cameras()[0]
    show_video = True
    highlight_color = (255, 0, 0)
    window_width, window_height = 640, 480 # info.current_w, info.current_h
    capture_width, capture_height = 640, 480
    surface = pygame.display.set_mode((window_width, window_height))
    capture_surface = Cell(pygame.Surface((capture_width, capture_height)))
    capture_ndarray = capture_surface.derive(lambda x: pygame.surfarray.array3d(x).swapaxes(0, 1))
    capture_grayscale = capture_ndarray.derive(lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY))
    face_recognition = cv2.CascadeClassifier(f'{cv2.data.haarcascades}haarcascade_frontalface_default.xml')

    countdown = Countdown(1 / capture_fps)
    with Capturer(camera, capture_surface) as capture:
        active = True
        while active:
            elapsed_seconds = clock.tick(fps) / 1000
            countdown.tick(elapsed_seconds)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        show_video = not show_video

            if countdown.ready:
                countdown.reset()
                capture()

                if decoded := decode(capture_ndarray.value):
                    data = decoded[0]
                    polygon = data.polygon
                    pygame.draw.polygon(capture_surface.value, highlight_color, [(p.x, p.y) for p in polygon], width=2)

                    faces = face_recognition.detectMultiScale(
                            capture_grayscale.value,
                            scaleFactor=1.1,
                            minNeighbors=5)
                    for (x, y, w, h) in faces:
                        rect = pygame.Rect(x, y, w, h)
                        pygame.draw.rect(capture_surface.value, highlight_color, rect, width=2)

                    print(decoded)

                if show_video:
                    surface.blit(capture_surface.value, (0, 0))
                pygame.display.flip()


@click.group()
def config():
    pass


@click.command()
def show():
    settings = load_settings(Path.home().joinpath('absentees.config.json'))
    print(json.dumps(settings.data, indent=4, sort_keys=True))


cli.add_command(tui)
cli.add_command(gui)
cli.add_command(config)
config.add_command(show)

if __name__ == '__main__':
    cli()
