import logging
import pygame
import pygame.camera


pygame.init()
pygame.camera.init()


class Capturer:
    """
    Allows to identify Capturer subclasses using isinstance
    """
    pass


class VideoCapturerHandle:
    pass


class LambdaHandle(VideoCapturerHandle):
    def __init__(self, func):
        self.__func = func

    def capture(self, target_surface):
        return self.__func(target_surface)


class VideoCapturer(Capturer):
    def __init__(self, camera_name, size):
        format = 'RGB'
        logging.info(f"Creating pygame camera with name={camera_name}, size={size}, format={format}")
        self.__camera = pygame.camera.Camera(camera_name, size, format)

    def __enter__(self):
        self.__camera.start()
        return LambdaHandle(self.__capture)

    def __exit__(self, exception, value, traceback):
        self.__camera.stop()

    def __capture(self, target_surface):
        self.__camera.get_image(target_surface)

    @staticmethod
    def cameras():
        return pygame.camera.list_cameras()

    @staticmethod
    def default_camera_name():
        return VideoCapturer.cameras()[0]

    @staticmethod
    def default_camera(size):
        return VideoCapturer(VideoCapturer.default_camera_name(), size)


class DummyCapturer(Capturer):
    def __init__(self):
        self.__counter = 0
        self.__font = pygame.font.SysFont(None, 64)

    def __enter__(self):
        return LambdaHandle(self.capture)

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


class InjectingCapturer(Capturer):
    def __init__(self, capturer):
        assert isinstance(capturer, Capturer)
        self.__capturer = capturer
        self.__injected = None
        self.__count = 0

    def __enter__(self):
        self.__handle = self.__capturer.__enter__()
        return LambdaHandle(self.capture)

    def __exit__(self, exception, value, traceback):
        self.__handle = None
        return self.__capturer.__exit__(exception, value, traceback)

    def inject(self, surface, count=1):
        self.__injected = surface
        self.__count = count

    def capture(self, target_surface):
        if self.__injected:
            target_surface.blit(self.__injected, (0, 0))
            self.__count -= 1
            if self.__count == 0:
                self.__injected = None
        else:
            self.__handle.capture(target_surface)
