from attendances.tools.analyzing import FrameAnalyzer


class AnalyzerNode:
    def __init__(self, analyzer):
        assert isinstance(analyzer, FrameAnalyzer)
        self.__analyzer = analyzer
        self.__observers = []

    def analyze(self, image):
        results = self.__analyzer.analyze(image)
        self.__notify_observers(results)

    def on_analysis(self, observer):
        self.__observers.append(observer)

    def __notify_observers(self, results):
        for observer in self.__observers:
            observer(results)

