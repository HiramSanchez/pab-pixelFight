from dataclasses import dataclass

import pygame

from pixel_fight.combat.attack import AttackDefinition, AttackKind, SpecialEffect

@dataclass(frozen=True)
class ControlScheme:
    left: int
    right: int
    jump: int
    block: int
    attack_1: int
    attack_2: int
    special: int


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

ROUND_TIME_LIMIT = 94 * 1000
ROUND_OVER_COOLDOWN = 2000
SHOW_FIGHT_TIME = 1000

GREEN = (23, 193, 36)
RED = (163, 41, 41)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (190, 190, 190)
DARKGRAY = (100, 100, 100)
BLUE = (4, 28, 49)
CYAN = (15, 158, 234)

FIGHTERS = [
    {"name": "Raruto", "asset_dir": "Raruto", "size": 128, "scale": 1.6, "offset": [34, 15], "freeze_offset": [-55, -23], "hurtbox": [80, 180], "animation_steps": [6, 8, 8, 10, 3, 4, 4, 2, 3, 4]},
    {"name": "Starlight", "asset_dir": "Starlight", "size": 128, "scale": 2.1, "offset": [45, 41], "freeze_offset": [-95, -87], "hurtbox": [80, 180], "animation_steps": [7, 7, 8, 8, 4, 10, 10, 7, 3, 6]},
    {"name": "Onichan", "asset_dir": "onichan", "size": 128, "scale": 2, "offset": [44, 38], "freeze_offset": [-88, -75], "hurtbox": [80, 180], "animation_steps": [5, 6, 7, 8, 4, 4, 4, 4, 3, 6]},
    {"name": "Bam", "asset_dir": "bam", "size": 128, "scale": 1.8, "offset": [40, 27], "freeze_offset": [-73, -50], "hurtbox": [80, 180], "animation_steps": [6, 8, 8, 12, 6, 4, 3, 2, 2, 4]},
]

PLAYER_CONTROLS = {
    1: ControlScheme(
        left=pygame.K_a,
        right=pygame.K_d,
        jump=pygame.K_w,
        block=pygame.K_1,
        attack_1=pygame.K_2,
        attack_2=pygame.K_3,
        special=pygame.K_4,
    ),
    2: ControlScheme(
        left=pygame.K_LEFT,
        right=pygame.K_RIGHT,
        jump=pygame.K_UP,
        block=pygame.K_m,
        attack_1=pygame.K_COMMA,
        attack_2=pygame.K_PERIOD,
        special=pygame.K_SLASH,
    ),
}


def normal_attack(kind, action, damage, width, phases):
    return AttackDefinition(
        kind=kind,
        animation_action=action,
        damage=damage,
        energy_cost=0,
        hitbox_width=width,
        startup_frames=phases[0],
        active_frames=phases[1],
        recovery_frames=phases[2],
        energy_on_hit=20,
        energy_on_block=10,
    )


def special_attack(damage, width, phases, effect, heal=0):
    return AttackDefinition(
        kind=AttackKind.SPECIAL,
        animation_action=6,
        damage=damage,
        energy_cost=100,
        hitbox_width=width,
        startup_frames=phases[0],
        active_frames=phases[1],
        recovery_frames=phases[2],
        effect=effect,
        heal=heal,
    )


ATTACK_DEFINITIONS = {
    "Raruto": {
        AttackKind.NORMAL_1: normal_attack(AttackKind.NORMAL_1, 4, 10, 1.5, (1, 1, 1)),
        AttackKind.NORMAL_2: normal_attack(AttackKind.NORMAL_2, 5, 6, 1.9, (1, 1, 2)),
        AttackKind.SPECIAL: special_attack(0, 1.5, (1, 1, 2), SpecialEffect.BURN),
    },
    "Starlight": {
        AttackKind.NORMAL_1: normal_attack(AttackKind.NORMAL_1, 4, 10, 1.5, (1, 1, 2)),
        AttackKind.NORMAL_2: normal_attack(AttackKind.NORMAL_2, 5, 6, 1.9, (3, 2, 5)),
        AttackKind.SPECIAL: special_attack(20, 1.5, (3, 2, 5), SpecialEffect.HEAL, heal=15),
    },
    "Onichan": {
        AttackKind.NORMAL_1: normal_attack(AttackKind.NORMAL_1, 4, 10, 1.5, (1, 1, 2)),
        AttackKind.NORMAL_2: normal_attack(AttackKind.NORMAL_2, 5, 6, 1.9, (1, 1, 2)),
        AttackKind.SPECIAL: special_attack(15, 1.5, (1, 1, 2), SpecialEffect.FREEZE),
    },
    "Bam": {
        AttackKind.NORMAL_1: normal_attack(AttackKind.NORMAL_1, 4, 10, 1.5, (2, 1, 3)),
        AttackKind.NORMAL_2: normal_attack(AttackKind.NORMAL_2, 5, 6, 1.9, (1, 1, 2)),
        AttackKind.SPECIAL: special_attack(35, 3.25, (0, 3, 0), SpecialEffect.DASH),
    },
}

DEFAULT_ATTACK_DEFINITIONS = ATTACK_DEFINITIONS["Raruto"]
