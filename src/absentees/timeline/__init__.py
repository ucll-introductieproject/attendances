from absentees.timeline.action import Action
from absentees.timeline.cyclic import Cyclic
from absentees.timeline.delay import Delay
from absentees.timeline.sequence import Sequence
from absentees.timeline.parallel import Parallel


def repeat(callback, time_interval):
    action = Action(callback)
    delay = Delay(time_interval)
    sequence = Sequence(delay, action)
    return Cyclic(sequence)
