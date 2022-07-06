import pygame
import logging
import cv2
from absentees.countdown import Countdown
from absentees.cells import Cell
from absentees.capturer import Capturer
from absentees.face import FaceDetector
from absentees.qr import QRScanner


def get_window_size(settings):
    info = pygame.display.Info()
    window_width, window_height = settings['window.width'], settings['window.height']
    if window_width == 0:
        window_width = info.current_w
    if window_height == 0:
        window_height = info.current_h
    return window_width, window_height


def run(settings):
    pygame.init()
    fps = settings['frame-rate']
    capture_fps = settings['capture.rate']
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    camera = Capturer.default_camera()
    show_video = True
    highlight_color = (255, 0, 0)
    window_size = get_window_size(settings)
    capture_width, capture_height = settings['capture.width'], settings['capture.height']

    logging.debug(f'Creating window with size {window_size[0]}x{window_size[1]}')
    surface = pygame.display.set_mode(window_size)
    capture_surface = Cell(pygame.Surface((capture_width, capture_height)))
    capture_ndarray = capture_surface.derive(lambda x: pygame.surfarray.array3d(x).swapaxes(0, 1))
    capture_grayscale = capture_ndarray.derive(lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY))
    face_detector = FaceDetector()
    qr_scanner = QRScanner()

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

                if decoded := qr_scanner.scan(capture_ndarray.value):
                    data = decoded[0]
                    pygame.draw.polygon(capture_surface.value, highlight_color, data.polygon, width=2)

                    faces = face_detector.detect(capture_grayscale.value)
                    for (x, y, w, h) in faces:
                        rect = pygame.Rect(x, y, w, h)
                        pygame.draw.rect(capture_surface.value, highlight_color, rect, width=2)

                    print(data.data)

                if show_video:
                    surface.blit(capture_surface.value, (0, 0))
                pygame.display.flip()
