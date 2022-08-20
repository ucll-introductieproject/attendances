from attendances.tools.capturing import VideoCapturerHandle


class CapturingNode:
    def __init__(self, capturer_handle, surface):
        assert isinstance(capturer_handle, VideoCapturerHandle)
        self.__capturer_handle = capturer_handle
        self.__surface = surface
        self.__observers = []

    def on_captured(self, observer):
        self.__observers.append(observer)

    def capture(self):
        self.__capturer_handle.capture(self.__surface)
        self.__notify_observers()

    def __notify_observers(self):
        for observer in self.__observers:
            observer(self.__surface)
