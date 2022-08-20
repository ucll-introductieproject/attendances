from attendances.pipeline.node import Node


class SkipperNode(Node):
    def __init__(self, n):
        super().__init__()
        self.__n = n
        self.__count = 0

    def perform(self, *args, **kwargs):
        self.__count += 1
        if self.__count == self.__n:
            self.__count = 0
            self._notify_observers(*args, **kwargs)
