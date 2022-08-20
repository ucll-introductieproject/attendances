from attendances.pipeline.node import Node


class TransformerNode(Node):
    def __init__(self, transformer):
        super().__init__()
        self.__transformer = transformer

    def transform(self, image):
        results = self.__transformer(image)
        if results:
            self._notify_observers(results)
