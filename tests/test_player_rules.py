import pygame
import pytest

from combat.attack import AttackKind
from player import (
    ACTION_ATTACK_1,
    ACTION_DEATH,
    ACTION_HIT,
    ACTION_IDLE,
    ATTACK_COOLDOWN_FRAMES,
)
from settings import ATTACK_DEFINITIONS, PLAYER_CONTROLS


def test_update_clamps_health_and_energy_upper_bounds(player_factory):
    player = player_factory()
    player.health = 130
    player.energy = 140

    player.update(now=0)

    assert player.health == 100
    assert player.energy == 100


def test_update_clamps_lethal_health_and_selects_death(player_factory):
    player = player_factory()
    player.health = -5

    player.update(now=0)

    assert player.health == 0
    assert player.alive is False
    assert player.action == ACTION_DEATH


def test_special_is_rejected_without_enough_energy(
    player_factory,
    pressed_keys,
):
    player = player_factory(name="Raruto")
    target = player_factory(player_number=2, x=260)
    player.energy = 99

    player.handle_input(
        pressed_keys(PLAYER_CONTROLS[1].special),
        None,
        target,
    )

    assert player.attacking is False
    assert player.active_attack is None
    assert player.energy == 99
    assert target.health == 100


@pytest.mark.parametrize("blocked_by", ["cooldown", "active_attack"])
def test_attack_rejection_preserves_current_state(player_factory, blocked_by):
    player = player_factory(name="Raruto")
    target = player_factory(player_number=2, x=260)
    definition = ATTACK_DEFINITIONS["Raruto"][AttackKind.NORMAL_1]

    if blocked_by == "cooldown":
        player.attack_cooldown = 1
    else:
        assert player.begin_attack(definition, target) is True

    energy_before = player.energy
    active_before = player.active_attack
    assert player.begin_attack(definition, target) is False
    assert player.energy == energy_before
    assert player.active_attack is active_before


def test_missed_active_frame_can_connect_on_later_active_frame(player_factory):
    player = player_factory(name="Starlight")
    target = player_factory(player_number=2, x=500)
    definition = ATTACK_DEFINITIONS["Starlight"][AttackKind.NORMAL_2]
    assert player.begin_attack(definition, target) is True
    player.frame_index = definition.startup_frames

    assert player.resolve_active_attack() is False
    target.rect.x = 260
    player.frame_index += 1

    assert player.resolve_active_attack() is True
    assert target.health == 94


def test_attack_animation_cleanup_clears_activation_state(player_factory):
    player = player_factory(name="Raruto")
    target = player_factory(player_number=2, x=260)
    definition = ATTACK_DEFINITIONS["Raruto"][AttackKind.NORMAL_1]
    assert player.begin_attack(definition, target) is True
    player.action = ACTION_ATTACK_1
    player.frame_index = len(player.animation_list[ACTION_ATTACK_1])

    player.finish_animation()

    assert player.attacking is False
    assert player.active_attack is None
    assert player.attack_target is None
    assert player.attack_has_hit is False
    assert player.attack_cooldown == ATTACK_COOLDOWN_FRAMES


def test_dash_expiry_clears_travelling_attack(
    player_factory,
    monkeypatch,
):
    player = player_factory(name="Bam")
    target = player_factory(player_number=2, x=700)
    definition = ATTACK_DEFINITIONS["Bam"][AttackKind.SPECIAL]
    player.energy = 100
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 0)
    assert player.begin_attack(definition, target) is True

    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 200)
    player.update_dash(0, round_over=False, delta_time_ms=16)

    assert player.dashing is False
    assert player.active_attack is None
    assert player.attack_target is None
    assert player.attack_cooldown == ATTACK_COOLDOWN_FRAMES


def test_freeze_locks_and_then_releases_animation_frame(player_factory):
    player = player_factory(animation_steps=[2] * 10)
    player.action = ACTION_HIT
    player.frame_index = 1
    player.hit = True
    player.apply_freeze(100)

    player.update(now=200)
    assert player.action == ACTION_HIT
    assert player.frame_index == 1

    player.update(now=3100)
    assert player.frozen is False
    assert player.action == ACTION_HIT


def test_finished_hit_animation_returns_to_idle_on_next_selection(
    player_factory,
):
    player = player_factory()
    player.action = ACTION_HIT
    player.hit = True
    player.attacking = True
    player.frame_index = len(player.animation_list[ACTION_HIT])

    player.finish_animation()
    player.select_animation_action()

    assert player.action == ACTION_IDLE
    assert player.hit is False
    assert player.attacking is False
