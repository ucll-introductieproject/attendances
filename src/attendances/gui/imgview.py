class ImageViewer:
    def __init__(self, image_cell, position):
        self.__dirty = True
        self.__image_cell = image_cell
        self.__image_cell.on_value_changed(self.__make_dirty)
        self.__position = position

    def __make_dirty(self):
        self.__dirty = True

    def tick(self, elapsed_seconds):
        pass

    def render(self, surface):
        if self.__dirty:
            surface.blit(self.__image_cell.value, self.__position)
            self.__dirty = False
