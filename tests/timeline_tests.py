from re import X
from attendances.timeline import Action, Delay, Sequence, Cyclic, repeat
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


def test_sequence():
    def increment_x():
        nonlocal x
        x += 1

    x = 0
    timeline = Sequence(Delay(5), Action(increment_x)).instantiate()
    assert x == 0
    assert timeline.tick(2) == 0
    assert x == 0
    assert timeline.tick(2) == 0
    assert x == 0
    assert timeline.tick(2) == 1
    assert x == 1


def test_cyclic():
    def increment_x():
        nonlocal x
        x += 1

    x = 0
    timeline = Cyclic(Sequence(Delay(5), Action(increment_x))).instantiate()
    assert x == 0
    assert timeline.tick(2) == 0
    assert x == 0
    assert timeline.tick(2) == 0
    assert x == 0
    assert timeline.tick(2) == 0
    assert x == 1
    assert timeline.tick(2) == 0
    assert x == 1
    assert timeline.tick(2.1) == 0
    assert x == 2


def test_repeat():
    def increment_x():
        nonlocal x
        x += 1

    x = 0
    timeline = repeat(increment_x, 5).instantiate()
    assert x == 0
    assert timeline.tick(2) == 0
    assert x == 0
    assert timeline.tick(2) == 0
    assert x == 0
    assert timeline.tick(2) == 0
    assert x == 1
    assert timeline.tick(2) == 0
    assert x == 1
    assert timeline.tick(2.1) == 0
    assert x == 2
