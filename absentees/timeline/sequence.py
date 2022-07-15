class Sequence:
    def __init__(self, *children):
        self.__children = children

    def instantiate(self):
        return _SequenceInstance(self.__children)


class _SequenceInstance:
    def __init__(self, children):
        self.__instances = [child.instantiate() for child in children]
        self.__index = 0

    def tick(self, elapsed_seconds):
        while self.__index < len(self.__instances) and (elapsed_seconds := self.__instances[self.__index].tick(elapsed_seconds)) > 0:
            self.__index += 1
        return elapsed_seconds
