import pytest

from status_effect import (
    BURN_TINT,
    FREEZE_TINT,
    BurnEffect,
    TimedEffect,
    active_tints,
)


def test_timed_effect_expires_at_configured_duration():
    effect = TimedEffect(duration_ms=3000)
    effect.start(100)

    assert effect.update(3099) is False
    assert effect.active is True
    assert effect.update(3100) is True
    assert effect.active is False


def test_timed_effect_restart_refreshes_duration():
    effect = TimedEffect(duration_ms=3000)
    effect.start(0)
    effect.start(2000)

    assert effect.update(4999) is False
    assert effect.update(5000) is True


@pytest.mark.parametrize(
    ("now", "damage", "ticks"),
    [
        (1999, 0, 0),
        (2000, 10, 1),
        (3999, 0, 1),
        (4000, 10, 2),
        (6000, 10, 3),
    ],
)
def test_burn_ticks_at_two_second_intervals(now, damage, ticks):
    effect = BurnEffect()
    effect.start(0)

    observed_damage = 0
    checkpoints = [time for time in (1999, 2000, 3999, 4000, 6000) if time <= now]
    for checkpoint in checkpoints:
        observed_damage = effect.update(checkpoint)

    assert observed_damage == damage
    assert effect.ticks_applied == ticks


def test_burn_catches_up_all_due_ticks_after_lag():
    effect = BurnEffect()
    effect.start(0)

    assert effect.update(7000) == 30
    assert effect.ticks_applied == 3
    assert effect.active is False
    assert effect.update(9000) == 0


def test_reapplying_burn_restarts_ticks():
    effect = BurnEffect()
    effect.start(0)
    assert effect.update(2000) == 10

    effect.start(2500)

    assert effect.ticks_applied == 0
    assert effect.update(4499) == 0
    assert effect.update(4500) == 10


def test_burn_and_freeze_tints_can_coexist_with_freeze_on_top():
    assert active_tints(burned=True, frozen=True) == (BURN_TINT, FREEZE_TINT)
