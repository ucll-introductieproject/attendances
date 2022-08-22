from attendances.pipeline.node import Node
from attendances.tools.analyzing import FrameAnalyzer
from attendances.imaging.image import Image
from attendances.countdown import Countdown
import logging


class AnalyzerNode(Node):
    def __init__(self, transformations, analyzer, countdown_duration=1):
        assert isinstance(analyzer, FrameAnalyzer)
        super().__init__()
        self.__analyzer = analyzer
        self.__transformations = transformations
        self.__countdown = Countdown(countdown_duration)

    def analyze(self, image):
        if self.__countdown.ready:
            self.__countdown.reset()
            assert isinstance(image, Image), f'was {type(image)}'
            for transformation in self.__transformations:
                transformed_image = getattr(image, transformation)
                analysis = self.__analyzer.analyze(transformed_image)
                if analysis:
                    logging.info(f'Found {analysis}')
                    self._notify_observers(analysis)
                    break

    def tick(self, elapsed_seconds):
        self.__countdown.tick(elapsed_seconds)
