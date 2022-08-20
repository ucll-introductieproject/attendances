from attendances.pipeline.node import Node
from attendances.tools.capturing import VideoCapturerHandle


class CapturingNode(Node):
    def __init__(self, capturer_handle, surface):
        assert isinstance(capturer_handle, VideoCapturerHandle)
        super().__init__()
        self.__capturer_handle = capturer_handle
        self.__surface = surface

    def capture(self):
        self.__capturer_handle.capture(self.__surface)
        self._notify_observers(self.__surface)
