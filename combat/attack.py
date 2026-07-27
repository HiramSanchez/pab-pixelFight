from dataclasses import dataclass
from enum import Enum, IntEnum

import pygame


class AttackKind(IntEnum):
    NORMAL_1 = 1
    NORMAL_2 = 2
    SPECIAL = 3


class SpecialEffect(Enum):
    NONE = "none"
    BURN = "burn"
    HEAL = "heal"
    FREEZE = "freeze"
    DASH = "dash"


@dataclass(frozen=True)
class AttackDefinition:
    kind: AttackKind
    animation_action: int
    damage: int
    energy_cost: int
    hitbox_width: float
    startup_frames: int
    active_frames: int
    recovery_frames: int
    energy_on_hit: int = 0
    energy_on_block: int = 0
    effect: SpecialEffect = SpecialEffect.NONE
    heal: int = 0

    @property
    def total_frames(self):
        return self.startup_frames + self.active_frames + self.recovery_frames

    @property
    def active_frame_range(self):
        start = self.startup_frames
        return range(start, start + self.active_frames)

    @property
    def travels_with_dash(self):
        return self.effect is SpecialEffect.DASH

    def is_active(self, frame_index, dashing=False):
        if self.travels_with_dash:
            return dashing
        return frame_index in self.active_frame_range

    def create_hitbox(self, body_rect, flipped):
        width = body_rect.width * self.hitbox_width
        return pygame.Rect(
            body_rect.centerx - width * flipped,
            body_rect.y,
            width,
            body_rect.height,
        )
