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


class Countdown:
    def __init__(self, duration):
        self.__duration = duration
        self.__time_left = duration

    def tick(self, elapsed_seconds):
        self.__time_left = max(0, self.__time_left - elapsed_seconds)

    @property
    def ready(self):
        return self.__time_left == 0

    def reset(self):
        self.__time_left = self.__duration


@click.command()
@click.option('--fps', help='Target frame rate', default=30)
@click.option('--cfps', help='Capture frame rate', default=2)
def gui(fps, cfps):
    capture_fps = cfps
    pygame.init()
    pygame.camera.init()
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    font = pygame.font.SysFont(None, 48)
    show_video = True
    highlight_color = (255, 0, 0)
    window_width, window_height = 640, 480 # info.current_w, info.current_h
    capture_width, capture_height = 640, 480
    surface = pygame.display.set_mode((window_width, window_height))
    capture_surface = pygame.Surface((capture_width, capture_height))
    camera = pygame.camera.Camera(pygame.camera.list_cameras()[0], (capture_width, capture_height), 'RGB')
    face_recognition = cv2.CascadeClassifier(f'{cv2.data.haarcascades}haarcascade_frontalface_default.xml')
    camera.start()
    countdown = Countdown(1 / capture_fps)
    try:
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
                camera.get_image(capture_surface)

                converted = pygame.surfarray.array3d(capture_surface).swapaxes(0, 1)


                if decoded := decode(converted):
                    data = decoded[0]
                    polygon = data.polygon
                    pygame.draw.polygon(capture_surface, highlight_color, [(p.x, p.y) for p in polygon], width=2)

                    gray = cv2.cvtColor(converted, cv2.COLOR_BGR2GRAY)
                    faces = face_recognition.detectMultiScale(
                            gray,
                            scaleFactor=1.1,
                            minNeighbors=5)
                    for (x, y, w, h) in faces:
                        rect = pygame.Rect(x, y, w, h)
                        pygame.draw.rect(capture_surface, highlight_color, rect, width=2)

                    print(decoded)

                if show_video:
                    surface.blit(capture_surface, (0, 0))
                pygame.display.flip()
    finally:
        camera.stop()
        pass


cli.add_command(tui)
cli.add_command(gui)

if __name__ == '__main__':
    cli()
