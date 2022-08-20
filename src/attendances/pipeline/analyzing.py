from attendances.pipeline.node import Node
from attendances.tools.analyzing import FrameAnalyzer


class AnalyzerNode(Node):
    def __init__(self, analyzer):
        assert isinstance(analyzer, FrameAnalyzer)
        super().__init__()
        self.__analyzer = analyzer

    def analyze(self, image):
        results = self.__analyzer.analyze(image)
        if results:
            self._notify_observers(results)
