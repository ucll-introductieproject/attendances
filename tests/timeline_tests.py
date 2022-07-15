from re import X
from absentees.timeline import Action, Delay
import pytest


@pytest.mark.parametrize("elapsed", [0, 1, 2, 2.5, 45.6])
def test_action(elapsed):
    def increment_x():
        nonlocal x
        x += 1

    x = 0
    timeline = Action(increment_x).instantiate()
    leftover = timeline.tick(elapsed)
    assert leftover == elapsed
    assert x == 1


def test_delay():
    timeline = Delay(5).instantiate()
    assert timeline.tick(1) == 0
    assert timeline.tick(2) == 0
    assert timeline.tick(3) == 1
