from attendances.tools.capturing import Capturer


class FrameSource:
    def __init__(self, capturer):
        assert isinstance(capturer, Capturer)
        self.__capturer = capturer

    # def capture(self):
    #     self.__capturer.