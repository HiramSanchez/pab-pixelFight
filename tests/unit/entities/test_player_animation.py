import pygame
import pytest

from pixel_fight.entities.player import (
    ACTION_ATTACK_1,
    ACTION_ATTACK_2,
    ACTION_BLOCK,
    ACTION_DEATH,
    ACTION_HIT,
    ACTION_IDLE,
    ACTION_JUMP,
    ACTION_RUN,
    ACTION_SPECIAL,
    ATTACK_NORMAL_1,
    ATTACK_NORMAL_2,
    ATTACK_SPECIAL,
    Player,
)


@pytest.fixture(scope="module", autouse=True)
def pygame_runtime():
    pygame.init()
    yield
    pygame.quit()


def make_player():
    data = {
        "name": "Test",
        "size": 1,
        "scale": 1,
        "offset": [0, 0],
    }
    animations = [[pygame.Surface((1, 1), pygame.SRCALPHA)] for _ in range(10)]
    return Player(1, 200, 310, False, data, None, [1] * 10, animations)


@pytest.mark.parametrize(
    ("changes", "expected_action"),
    [
        ({"alive": False, "blocking": True}, ACTION_DEATH),
        ({"blocking": True, "hit": True}, ACTION_BLOCK),
        ({"hit": True, "attacking": True}, ACTION_HIT),
        (
            {"attacking": True, "attack_type": ATTACK_NORMAL_1},
            ACTION_ATTACK_1,
        ),
        (
            {"attacking": True, "attack_type": ATTACK_NORMAL_2},
            ACTION_ATTACK_2,
        ),
        (
            {"attacking": True, "attack_type": ATTACK_SPECIAL},
            ACTION_SPECIAL,
        ),
        ({"jump": True, "running": True}, ACTION_JUMP),
        ({"running": True}, ACTION_RUN),
        ({}, ACTION_IDLE),
    ],
)
def test_animation_priority_is_preserved(changes, expected_action):
    player = make_player()
    for name, value in changes.items():
        setattr(player, name, value)

    player.select_animation_action()

    assert player.action == expected_action


def test_attack_animation_completion_restores_control_and_cooldown():
    player = make_player()
    player.attacking = True
    player.action = ACTION_ATTACK_1
    player.frame_index = len(player.animation_list[ACTION_ATTACK_1])

    player.finish_animation()

    assert player.frame_index == 0
    assert player.attacking is False
    assert player.attack_cooldown == 30


def test_hit_animation_completion_clears_hit_and_attack():
    player = make_player()
    player.hit = True
    player.attacking = True
    player.action = ACTION_HIT
    player.frame_index = len(player.animation_list[ACTION_HIT])

    player.finish_animation()

    assert player.hit is False
    assert player.attacking is False
    assert player.attack_cooldown == 30
