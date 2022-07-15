import pygame
import pygame.camera


pygame.init()
pygame.camera.init()


class VideoCapturer:
    def __init__(self, camera_name, size):
        self.__camera = pygame.camera.Camera(camera_name, size, 'RGB')

    def __enter__(self):
        self.__camera.start()
        return self.capture

    def __exit__(self, exception, value, traceback):
        self.__camera.stop()

    def capture(self, target_surface):
        self.__capture.get_image(target_surface)

    @staticmethod
    def cameras():
        return pygame.camera.list_cameras()

    @staticmethod
    def default_camera():
        return VideoCapturer.cameras()[0]


class DummyCapturer:
    def __init__(self):
        self.__counter = 0
        self.__font = pygame.font.SysFont(None, 64)

    def __enter__(self):
        return self.capture

    def __exit__(self, exception, value, traceback):
        pass

    def capture(self, target_surface):
        target_surface.fill((0, 0, 0))
        text = self.__font.render(str(self.__counter), True, (255, 255, 255))
        surface_width, surface_height = target_surface.get_size()
        text_width, text_height = text.get_size()
        x = (surface_width - text_width) / 2
        y = (surface_height - text_height) / 2
        target_surface.blit(text, (x, y))
        self.__counter += 1
