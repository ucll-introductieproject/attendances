from attendances.pipeline.node import Node
from attendances.imaging.image import Image


class ImageWrapper(Node):
    def __init__(self):
        super().__init__()

    def wrap(self, surface):
        self._notify_observers(Image(surface.copy()))
