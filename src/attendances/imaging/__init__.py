import pygame
import numpy
import cv2


def to_grayscale(surface):
    pixels = pygame.surfarray.array3d(surface)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
    _, pixels = cv2.threshold(pixels, 127, 255, cv2.THRESH_BINARY)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_GRAY2BGR)
    return pygame.surfarray.make_surface(pixels)


def to_grayscale_adaptive(surface):
    pixels = pygame.surfarray.array3d(surface)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
    pixels = cv2.adaptiveThreshold(pixels, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    pixels = cv2.cvtColor(pixels, cv2.COLOR_GRAY2BGR)
    return pygame.surfarray.make_surface(pixels)
