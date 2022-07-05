import pygame.camera


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