import pygame
import pytest

from player import (
    ATTACK_COOLDOWN_FRAMES,
    ATTACK_NORMAL_1,
    ATTACK_NORMAL_2,
    JUMP_VELOCITY,
    MOVE_SPEED,
    Player,
)
from settings import PLAYER_CONTROLS


class PressedKeys:
    def __init__(self, *pressed):
        self.pressed = set(pressed)

    def __getitem__(self, key):
        return key in self.pressed


@pytest.fixture(scope="module", autouse=True)
def pygame_runtime():
    pygame.init()
    yield
    pygame.quit()


def make_player(player_number=1, x=200):
    data = {
        "name": "Test",
        "size": 1,
        "scale": 1,
        "offset": [0, 0],
    }
    animations = [[pygame.Surface((1, 1), pygame.SRCALPHA)] for _ in range(10)]
    return Player(
        player_number,
        x,
        310,
        player_number == 2,
        data,
        None,
        [1] * 10,
        animations,
    )


@pytest.mark.parametrize("player_number", [1, 2])
def test_control_scheme_moves_each_player_left_and_right(player_number):
    player = make_player(player_number)
    target = make_player(2 if player_number == 1 else 1, x=700)
    controls = PLAYER_CONTROLS[player_number]

    left_dx = player.handle_input(PressedKeys(controls.left), None, target)
    player.running = False
    right_dx = player.handle_input(PressedKeys(controls.right), None, target)

    assert left_dx == -MOVE_SPEED
    assert right_dx == MOVE_SPEED
    assert player.running is True


@pytest.mark.parametrize("player_number", [1, 2])
def test_right_input_keeps_original_precedence_when_both_are_held(player_number):
    player = make_player(player_number)
    target = make_player(2 if player_number == 1 else 1, x=700)
    controls = PLAYER_CONTROLS[player_number]

    dx = player.handle_input(
        PressedKeys(controls.left, controls.right),
        None,
        target,
    )

    assert dx == MOVE_SPEED


@pytest.mark.parametrize("player_number", [1, 2])
def test_block_prevents_movement_jump_and_attacks(player_number):
    player = make_player(player_number)
    target = make_player(2 if player_number == 1 else 1, x=260)
    controls = PLAYER_CONTROLS[player_number]

    dx = player.handle_input(
        PressedKeys(
            controls.block,
            controls.right,
            controls.jump,
            controls.attack_1,
        ),
        None,
        target,
    )

    assert dx == 0
    assert player.blocking is True
    assert player.jump is False
    assert player.attacking is False
    assert target.health == 100


@pytest.mark.parametrize("player_number", [1, 2])
def test_jump_uses_configured_key_and_original_velocity(player_number):
    player = make_player(player_number)
    target = make_player(2 if player_number == 1 else 1, x=700)

    player.handle_input(
        PressedKeys(PLAYER_CONTROLS[player_number].jump),
        None,
        target,
    )

    assert player.jump is True
    assert player.vel_y == JUMP_VELOCITY


@pytest.mark.parametrize("player_number", [1, 2])
def test_attack_key_mapping_is_symmetric(player_number):
    player = make_player(player_number)
    target_x = 260 if player_number == 1 else 140
    target = make_player(2 if player_number == 1 else 1, x=target_x)

    player.handle_input(
        PressedKeys(PLAYER_CONTROLS[player_number].attack_1),
        None,
        target,
    )

    assert player.attacking is True
    assert player.attack_type == ATTACK_NORMAL_1
    assert target.health == 90


@pytest.mark.parametrize(
    ("blocked", "expected_health", "expected_energy"),
    [
        (False, 90, 30),
        (True, 100, 20),
    ],
)
def test_attack_one_preserves_block_damage_and_energy_rules(
    blocked,
    expected_health,
    expected_energy,
):
    player = make_player(1)
    target = make_player(2, x=260)
    target.blocking = blocked
    player.attack_type = ATTACK_NORMAL_1

    player.attack(None, target)

    assert target.health == expected_health
    assert player.energy == expected_energy


def test_attack_two_preserves_damage():
    player = make_player(1)
    target = make_player(2, x=260)
    player.attack_type = ATTACK_NORMAL_2

    player.attack(None, target)

    assert target.health == 94
    assert player.energy == 30


def test_movement_is_limited_to_screen_and_floor():
    player = make_player(1, x=0)
    player.rect.y = 500
    player.vel_y = 5
    player.jump = True

    dx, dy = player.limit_movement(-MOVE_SPEED, 10, 1000, 600)

    assert dx == 0
    assert player.rect.bottom + dy == 490
    assert player.vel_y == 0
    assert player.jump is False


def test_cooldown_keeps_frame_based_countdown():
    player = make_player(1)
    player.attack_cooldown = ATTACK_COOLDOWN_FRAMES

    player.update_attack_cooldown()

    assert player.attack_cooldown == ATTACK_COOLDOWN_FRAMES - 1
