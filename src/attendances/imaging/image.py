from functools import cache, cached_property
import pygame
import cv2


class Image:
    def __init__(self, surface):
        self.__surface = surface

    @property
    def surface(self):
        return self.__surface

    @cached_property
    def array3d(self):
        return pygame.surfarray.array3d(self.surface)

    @cached_property
    def grayscale_array3d(self):
        return cv2.cvtColor(self.array3d, cv2.COLOR_BGR2GRAY)

    @cached_property
    def grayscale_surface(self):
        return self.__grayscale_array3d_to_surface(self.grayscale_array3d)

    @cached_property
    def bw_array3d(self):
        _, result = cv2.threshold(self.grayscale_array3d, 127, 255, cv2.THRESH_BINARY)
        return result

    @cached_property
    def bw_surface(self):
        return self.__grayscale_array3d_to_surface(self.bw_array3d)

    @cached_property
    def bw_mean_array3d(self):
        return cv2.adaptiveThreshold(self.grayscale_array3d, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    @cached_property
    def bw_mean_surface(self):
        return self.__grayscale_array3d_to_surface(self.bw_mean_array3d)

    @cached_property
    def bw_gaussian_array3d(self):
        return cv2.adaptiveThreshold(self.grayscale_array3d, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    @cached_property
    def bw_gaussian_surface(self):
        return self.__grayscale_array3d_to_surface(self.bw_gaussian_array3d)

    def __grayscale_array3d_to_surface(self, array3d):
        bgr = cv2.cvtColor(self.grayscale_array3d, cv2.COLOR_GRAY2BGR)
        return pygame.surfarray.make_surface(bgr)
