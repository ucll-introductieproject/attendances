from turtle import back
import pygame


class FpsViewer:
    def __init__(self, surface, fps):
        self.__surface = surface
        self.__font = pygame.font.SysFont(None, 16)
        self.__fps = fps
        self.__fps.on_value_changed(self.render)

    def render(self):
        antialias = True
        color = (255, 255, 255)
        background = (0, 0, 0)
        text = self.__font.render(str(round(self.__fps.value)), antialias, color, background)
        self.__surface.blit(text, (0, 0))
