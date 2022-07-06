import cv2
import pygame
from pyzbar.pyzbar import decode
from absentees.countdown import Countdown
from absentees.cells import Cell
from absentees.capturer import Capturer


def run(settings):
    fps = settings['frame-rate']
    capture_fps = settings['capture.rate']
    pygame.init()
    pygame.camera.init()
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    font = pygame.font.SysFont(None, 48)
    camera = Capturer.default_camera()
    show_video = True
    highlight_color = (255, 0, 0)
    window_width, window_height = 640, 480 # info.current_w, info.current_h
    capture_width, capture_height = settings['capture.width'], settings['capture.height']
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
