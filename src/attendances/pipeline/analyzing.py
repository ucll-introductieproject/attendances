from attendances.pipeline.node import Node
from attendances.tools.analyzing import FrameAnalyzer
from attendances.imaging.image import Image


class AnalyzerNode(Node):
    def __init__(self, transformations, analyzer):
        assert isinstance(analyzer, FrameAnalyzer)
        super().__init__()
        self.__analyzer = analyzer
        self.__transformations = transformations

    def analyze(self, image):
        assert isinstance(image, Image), f'was {type(image)}'
        for transformation in self.__transformations:
            transformed_image = getattr(image, transformation)
            analysis = self.__analyzer.analyze(transformed_image)
            if analysis:
                self._notify_observers(analysis)
                break
