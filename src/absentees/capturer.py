import pygame
import pygame.camera


pygame.init()
pygame.camera.init()


class VideoCapturer:
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
        return VideoCapturer.cameras()[0]


class DummyCapturer:
    def __init__(self, target_surface):
        self.__target_surface = target_surface
        self.__counter = 0
        self.__font = pygame.font.SysFont(None, 64)

    def __enter__(self):
        return self.__render_frame

    def __exit__(self, exception, value, traceback):
        pass

    def __render_frame(self):
        self.__target_surface.fill((0, 0, 0))
        text = self.__font.render(str(self.__counter), True, (255, 255, 255))
        surface_width, surface_height = self.__target_surface.get_size()
        text_width, text_height = text.get_size()
        x = (surface_width - text_width) / 2
        y = (surface_height - text_height) / 2
        self.__target_surface.blit(text, (x, y))
        self.__counter += 1
