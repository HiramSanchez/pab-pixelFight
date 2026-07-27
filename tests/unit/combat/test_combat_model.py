import pygame
import pytest

from pixel_fight.combat.attack import AttackKind
from pixel_fight.entities.player import Player
from pixel_fight.settings import ATTACK_DEFINITIONS, FIGHTERS


@pytest.fixture(scope="module", autouse=True)
def pygame_runtime():
    pygame.init()
    yield
    pygame.quit()


def make_player(name, player_number=1, x=200):
    data = next(fighter for fighter in FIGHTERS if fighter["name"] == name)
    animations = [
        [pygame.Surface((1, 1), pygame.SRCALPHA) for _ in range(frame_count)]
        for frame_count in data["animation_steps"]
    ]
    return Player(
        player_number,
        x,
        310,
        player_number == 2,
        data,
        None,
        data["animation_steps"],
        animations,
    )


def begin_and_set_frame(attacker, target, kind, frame_index):
    definition = attacker.attacks[kind]
    assert attacker.begin_attack(definition, target) is True
    attacker.frame_index = frame_index
    return definition


def test_every_fighter_has_explicit_hurtbox_and_three_attacks():
    for fighter in FIGHTERS:
        assert fighter["hurtbox"] == [80, 180]
        assert set(ATTACK_DEFINITIONS[fighter["name"]]) == set(AttackKind)


def test_attack_phases_match_configured_animation_lengths():
    fighters_by_name = {fighter["name"]: fighter for fighter in FIGHTERS}

    for name, attacks in ATTACK_DEFINITIONS.items():
        animation_steps = fighters_by_name[name]["animation_steps"]
        for attack in attacks.values():
            assert attack.total_frames == animation_steps[attack.animation_action]


def test_attack_only_hits_during_active_frames():
    attacker = make_player("Raruto")
    target = make_player("Raruto", player_number=2, x=260)
    definition = begin_and_set_frame(
        attacker,
        target,
        AttackKind.NORMAL_1,
        0,
    )

    assert attacker.resolve_active_attack() is False
    assert target.health == 100

    attacker.frame_index = definition.startup_frames
    assert attacker.resolve_active_attack() is True
    assert target.health == 90

    attacker.clear_active_attack()
    attacker.attacking = False
    begin_and_set_frame(
        attacker,
        target,
        AttackKind.NORMAL_1,
        definition.startup_frames + definition.active_frames,
    )
    assert attacker.resolve_active_attack() is False
    assert target.health == 90


def test_each_activation_can_hit_only_once():
    attacker = make_player("Starlight")
    target = make_player("Raruto", player_number=2, x=260)
    definition = begin_and_set_frame(
        attacker,
        target,
        AttackKind.NORMAL_2,
        attacker.attacks[AttackKind.NORMAL_2].startup_frames,
    )

    assert attacker.resolve_active_attack() is True
    attacker.frame_index = definition.startup_frames + 1
    assert attacker.resolve_active_attack() is False
    assert target.health == 94
    assert attacker.energy == 30


@pytest.mark.parametrize(
    ("flipped", "target_x"),
    [(False, 260), (True, 140)],
)
def test_hitbox_follows_facing(flipped, target_x):
    attacker = make_player("Raruto", x=200)
    attacker.flip = flipped
    target = make_player("Raruto", player_number=2, x=target_x)
    definition = begin_and_set_frame(
        attacker,
        target,
        AttackKind.NORMAL_1,
        attacker.attacks[AttackKind.NORMAL_1].startup_frames,
    )

    hitbox = definition.create_hitbox(attacker.rect, attacker.flip)
    assert hitbox.colliderect(target.rect)
    assert attacker.resolve_active_attack() is True


def test_hitbox_boundary_does_not_count_as_overlap():
    attacker = make_player("Raruto", x=200)
    target = make_player("Raruto", player_number=2, x=360)
    begin_and_set_frame(
        attacker,
        target,
        AttackKind.NORMAL_1,
        attacker.attacks[AttackKind.NORMAL_1].startup_frames,
    )

    assert attacker.resolve_active_attack() is False
    assert target.health == 100


@pytest.mark.parametrize(
    ("blocked", "health", "energy"),
    [(False, 90, 30), (True, 100, 20)],
)
def test_normal_attack_block_outcome_is_deterministic(blocked, health, energy):
    attacker = make_player("Raruto")
    target = make_player("Raruto", player_number=2, x=260)
    target.blocking = blocked
    begin_and_set_frame(
        attacker,
        target,
        AttackKind.NORMAL_1,
        attacker.attacks[AttackKind.NORMAL_1].startup_frames,
    )

    assert attacker.resolve_active_attack() is True
    assert target.health == health
    assert attacker.energy == energy


@pytest.mark.parametrize(
    ("name", "expected_health"),
    [("Raruto", 100), ("Starlight", 80), ("Onichan", 85)],
)
def test_stationary_specials_preserve_character_outcomes(name, expected_health):
    attacker = make_player(name)
    target = make_player("Raruto", player_number=2, x=260)
    attacker.energy = 100
    if name == "Starlight":
        attacker.health = 50
    definition = begin_and_set_frame(
        attacker,
        target,
        AttackKind.SPECIAL,
        attacker.attacks[AttackKind.SPECIAL].startup_frames,
    )

    assert attacker.energy == 0
    assert attacker.resolve_active_attack() is True
    assert target.health == expected_health
    if name == "Raruto":
        assert target.burned is True
    elif name == "Starlight":
        assert attacker.health == 65
    else:
        assert target.frozen is True
    assert definition.kind is AttackKind.SPECIAL


def test_blocked_special_spends_energy_without_damage_or_effect():
    attacker = make_player("Onichan")
    target = make_player("Raruto", player_number=2, x=260)
    attacker.energy = 100
    target.blocking = True
    begin_and_set_frame(
        attacker,
        target,
        AttackKind.SPECIAL,
        attacker.attacks[AttackKind.SPECIAL].startup_frames,
    )

    assert attacker.resolve_active_attack() is True
    assert attacker.energy == 0
    assert target.health == 100
    assert target.frozen is False


def test_bam_dash_hits_on_travel_and_only_once():
    attacker = make_player("Bam", x=0)
    target = make_player("Raruto", player_number=2, x=400)
    attacker.energy = 100
    definition = attacker.attacks[AttackKind.SPECIAL]

    assert attacker.begin_attack(definition, target) is True
    assert attacker.resolve_active_attack() is False

    attacker.rect.x = 160
    assert attacker.resolve_active_attack() is True
    assert target.health == 65
    attacker.rect.x = 200
    assert attacker.resolve_active_attack() is False
    assert target.health == 65
