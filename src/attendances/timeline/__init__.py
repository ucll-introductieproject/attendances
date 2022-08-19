from attendances.timeline.action import Action
from attendances.timeline.cyclic import Cyclic
from attendances.timeline.delay import Delay
from attendances.timeline.sequence import Sequence
from attendances.timeline.parallel import Parallel


def repeat(callback, time_interval):
    action = Action(callback)
    delay = Delay(time_interval)
    sequence = Sequence(delay, action)
    return Cyclic(sequence)
