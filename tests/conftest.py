import pygame
import pytest

from player import Player


class PressedKeys:
    def __init__(self, *pressed):
        self.pressed = set(pressed)

    def __getitem__(self, key):
        return key in self.pressed


@pytest.fixture
def pygame_runtime():
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def player_factory(pygame_runtime):
    def create(
        player_number=1,
        x=200,
        name="Test",
        animation_steps=None,
        attacks=None,
    ):
        steps = animation_steps or [1] * 10
        data = {
            "name": name,
            "size": 1,
            "scale": 1,
            "offset": [0, 0],
            "hurtbox": [80, 180],
        }
        animations = [
            [pygame.Surface((1, 1), pygame.SRCALPHA) for _ in range(count)]
            for count in steps
        ]
        return Player(
            player_number,
            x,
            310,
            player_number == 2,
            data,
            None,
            steps,
            animations,
            attacks=attacks,
        )

    return create


@pytest.fixture
def pressed_keys():
    return PressedKeys
