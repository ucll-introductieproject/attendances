from attendances.countdown import Countdown
from attendances.cells import Cell
from attendances.gui.imgview import ImageViewer


class FrameViewer:
    def __init__(self, model, position):
        self.__model = model
        self.__freeze_time = 2
        self.__countdown = Countdown(self.__freeze_time, 0)
        self.__image = Cell(self.__model.current_frame.value)
        self.__image_viewer = ImageViewer(self.__image, position)
        self.__model.frame_analysis.add_observer(self.__on_new_frame_analysis)

    def tick(self, elapsed_seconds):
        self.__countdown.tick(elapsed_seconds)
        if self.__countdown.ready:
            self.__image.value = self.__model.current_frame.value

    def render(self, surface):
        self.__image_viewer.render(surface)

    def __on_new_frame_analysis(self):
        self.__countdown.reset()
        self.__image.value = self.__model.frame_analysis.value[0]
