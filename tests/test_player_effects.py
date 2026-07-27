import pygame
import pytest

from player import Player


@pytest.fixture(scope="module", autouse=True)
def pygame_runtime():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def players(pygame_runtime):
    data = {
        "name": "Test",
        "size": 1,
        "scale": 1,
        "offset": [0, 0],
    }
    animations = [[pygame.Surface((1, 1), pygame.SRCALPHA)] for _ in range(10)]
    player = Player(1, 200, 310, False, data, None, [1] * 10, animations)
    target = Player(2, 700, 310, True, data, None, [1] * 10, animations)
    return player, target


def test_player_applies_all_overdue_burn_damage_under_lag(players):
    player, _ = players
    player.apply_burn(0)

    player.update(now=7000)

    assert player.health == 70
    assert player.burn_ticks == 3
    assert player.burned is False


def test_player_does_not_apply_burn_after_round_end(players):
    player, _ = players
    player.apply_burn(0)

    player.update(now=7000, round_active=False)

    assert player.health == 100
    assert player.burn_ticks == 0


def test_lethal_burn_marks_player_dead_in_same_update(players):
    player, _ = players
    player.health = 30
    player.apply_burn(0)

    player.update(now=7000)

    assert player.health == 0
    assert player.alive is False


def test_freeze_and_burn_can_be_active_together(players):
    player, _ = players

    player.apply_burn(0)
    player.apply_freeze(0)
    player.update(now=2999)

    assert player.burned is True
    assert player.frozen is True


def test_freeze_expires_after_three_seconds(players):
    player, _ = players
    player.apply_freeze(100)

    player.update(now=3099)
    assert player.frozen is True

    player.update(now=3100)
    assert player.frozen is False


@pytest.mark.parametrize("blocked_by", ["freeze", "death", "round_over"])
def test_dash_is_cancelled_by_incompatible_state(players, blocked_by):
    player, target = players
    player.dash_effect.start(pygame.time.get_ticks())

    if blocked_by == "freeze":
        player.apply_freeze(pygame.time.get_ticks())
    elif blocked_by == "death":
        player.alive = False

    player.move(
        1000,
        600,
        pygame.Surface((1, 1)),
        target,
        round_over=blocked_by == "round_over",
    )

    assert player.dashing is False


@pytest.mark.parametrize(
    ("delta_time_ms", "expected_distance"),
    [
        (1000 / 120, 10),
        (1000 / 60, 20),
        (1000 / 30, 40),
    ],
)
def test_dash_distance_uses_elapsed_time(players, delta_time_ms, expected_distance):
    player, target = players
    start_x = player.rect.x
    player.dash_effect.start(pygame.time.get_ticks())

    player.move(
        1000,
        600,
        pygame.Surface((1, 1)),
        target,
        round_over=False,
        delta_time_ms=delta_time_ms,
    )

    assert player.rect.x == start_x + expected_distance
