class Parallel:
    def __init__(self, *children):
        self.__children = children

    def instantiate(self):
        return _ParallelInstance(self.__children)


class _ParallelInstance:
    def __init__(self, children):
        self.__instances = [child.instantiate() for child in children]

    def tick(self, elapsed_seconds):
        return max(instance.tick(elapsed_seconds) for instance in self.__instances)
