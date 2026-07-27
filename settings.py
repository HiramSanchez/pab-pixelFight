from dataclasses import dataclass

import pygame


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
    {"name": "Raruto", "asset_dir": "Raruto", "size": 128, "scale": 1.6, "offset": [34, 15], "freeze_offset": [-55, -23], "animation_steps": [6, 8, 8, 10, 3, 4, 4, 2, 3, 4]},
    {"name": "Starlight", "asset_dir": "Starlight", "size": 128, "scale": 2.1, "offset": [45, 41], "freeze_offset": [-95, -87], "animation_steps": [7, 7, 8, 8, 4, 10, 10, 7, 3, 6]},
    {"name": "Onichan", "asset_dir": "onichan", "size": 128, "scale": 2, "offset": [44, 38], "freeze_offset": [-88, -75], "animation_steps": [5, 6, 7, 8, 4, 4, 4, 4, 3, 6]},
    {"name": "Bam", "asset_dir": "bam", "size": 128, "scale": 1.8, "offset": [40, 27], "freeze_offset": [-73, -50], "animation_steps": [6, 8, 8, 12, 6, 4, 3, 2, 2, 4]},
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
