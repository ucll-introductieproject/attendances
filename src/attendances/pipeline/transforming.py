class TransformerNode:
    def __init__(self, transformer):
        self.__transformer = transformer
        self.__observers = []

    def transform(self, image):
        results = self.__transformer(image)
        if results:
            self.__notify_observers(results)

    def on_transformed(self, observer):
        self.__observers.append(observer)

    def __notify_observers(self, *args, **kwargs):
        for observer in self.__observers:
            observer(*args, **kwargs)
