class Cyclic:
    def __init__(self, child):
        self.__child = child

    def instantiate(self):
        return _CyclicInstance(self.__child)


class _CyclicInstance:
    def __init__(self, child):
        self.__child = child
        self.__child_instance = child.instantiate()

    def tick(self, elapsed_seconds):
        while (elapsed_seconds := self.__child_instance.tick(elapsed_seconds)) > 0:
            self.__child_instance = self.__child.instantiate()
        return elapsed_seconds
