import pygame
import pygame.camera


pygame.init()
pygame.camera.init()

class Capturer:
    def __init__(self, camera_name, target_surface):
        assert isinstance(target_surface, pygame.Surface)

        width, height = target_surface.get_size()
        self.__camera = pygame.camera.Camera(camera_name, (width, height), 'RGB')
        self.__target = target_surface

    def __enter__(self):
        def capture():
            self.__camera.get_image(self.__target)
        self.__camera.start()
        return capture

    def __exit__(self, exception, value, traceback):
        self.__camera.stop()

    @staticmethod
    def cameras():
        return pygame.camera.list_cameras()

    @staticmethod
    def default_camera():
        return Capturer.cameras()[0]
