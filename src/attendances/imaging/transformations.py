import pygame
import cv2


_TRANSFORMATIONS = {}


def transformation(id):
    def receiver(f):
        _TRANSFORMATIONS[id] = f
        return f
    return receiver


@transformation('identity')
def identity(surface):
    return surface


@transformation('grayscale')
def to_grayscale(surface):
    pixels = pygame.surfarray.array3d(surface)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_GRAY2BGR)
    return pygame.surfarray.make_surface(pixels)


@transformation('bw')
def to_black_and_white(surface):
    pixels = pygame.surfarray.array3d(surface)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
    _, pixels = cv2.threshold(pixels, 127, 255, cv2.THRESH_BINARY)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_GRAY2BGR)
    return pygame.surfarray.make_surface(pixels)


@transformation('bw-mean')
def to_black_and_white_mean(surface):
    pixels = pygame.surfarray.array3d(surface)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
    pixels = cv2.adaptiveThreshold(pixels, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_GRAY2BGR)
    return pygame.surfarray.make_surface(pixels)


@transformation('bw-gaussian')
def to_black_and_white_gaussian(surface):
    pixels = pygame.surfarray.array3d(surface)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
    pixels = cv2.adaptiveThreshold(pixels, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_GRAY2BGR)
    return pygame.surfarray.make_surface(pixels)


def get_transformation_by_id(id):
    return _TRANSFORMATIONS[id]


def transformation_ids():
    return _TRANSFORMATIONS.keys()
