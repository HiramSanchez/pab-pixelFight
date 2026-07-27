import pygame

from pixel_fight.entities.player import Player


def test_new_player_has_fresh_round_state():
    pygame.init()
    data = {
        "name": "Test",
        "size": 1,
        "scale": 1,
        "offset": [0, 0],
    }
    sprite_sheet = pygame.Surface((1, 10), pygame.SRCALPHA)

    player = Player(1, 200, 310, False, data, sprite_sheet, [1] * 10)

    assert player.health == 100
    assert player.energy == 10
    assert player.alive is True
    assert player.attacking is False
    assert player.blocking is False
    assert player.hit is False
    assert player.dashing is False
    assert player.frozen is False
    assert player.burned is False
    assert player.burn_ticks == 0

    pygame.quit()


def test_player_can_reuse_preloaded_animations():
    pygame.init()
    data = {
        "name": "Test",
        "size": 1,
        "scale": 1,
        "offset": [0, 0],
    }
    animations = [[pygame.Surface((1, 1), pygame.SRCALPHA)] for _ in range(10)]

    player = Player(1, 200, 310, False, data, None, [1] * 10, animations)

    assert player.animation_list is animations

    pygame.quit()
