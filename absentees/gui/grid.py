import logging
import pygame


class Grid:
    def __init__(self, rectangle, grid_size):
        self.__rectangle = rectangle
        self.__grid_size = grid_size

    def child_rectangle(self, position):
        rectangle = self.__rectangle
        ncolumns, nrows = self.__grid_size
        width = rectangle.width // ncolumns
        height = rectangle.height // nrows
        hmargin = (rectangle.width - ncolumns * width) // 2
        vmargin = (rectangle.height - nrows * height) // 2
        px, py = position
        x = rectangle.left + hmargin + px * width
        y = rectangle.top + vmargin + py * height
        result = pygame.Rect(x, y, width, height)
        return result

    # def render(self, surface):
    #     grid_width, grid_height = self.__grid_size
    #     for y in range(grid_height):
    #         for x in range(grid_width):
    #             rect = self.__determine_child_rectangle((x, y))
    #             self.__render_child(surface, (x, y), rect)
