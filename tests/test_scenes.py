import os
import subprocess
import sys

import pygame
import pytest

from asset_manager import AssetManager
from game import GameContext
from scenes import SceneId
from scenes.battle_scene import BattleScene
from scenes.menu_scene import MenuScene
from scenes.selection_scene import SelectionScene
from settings import FIGHTERS


class FakeTime:
    def __init__(self):
        self.current = 0

    def __call__(self):
        return self.current


@pytest.fixture(scope="module")
def scene_context():
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    fake_time = FakeTime()
    context = GameContext(screen, AssetManager(), time_source=fake_time)
    yield context, fake_time
    pygame.quit()


def click(rect):
    return pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {"pos": rect.center, "button": 1},
    )


def test_importing_main_has_no_pygame_initialization_side_effect():
    environment = os.environ.copy()
    environment["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import pygame; "
                "assert not pygame.get_init(); "
                "import main; "
                "assert not pygame.get_init()"
            ),
        ],
        cwd=os.getcwd(),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_menu_transitions_to_selection(scene_context):
    context, _ = scene_context
    scene = MenuScene(context)
    scene.enter()

    scene.handle_event(click(scene.play_rect))

    assert scene.take_transition().target is SceneId.SELECTION


def test_menu_controls_overlay_opens_and_closes(scene_context):
    context, _ = scene_context
    scene = MenuScene(context)
    scene.enter()

    scene.handle_event(click(scene.controls_rect))
    assert scene.controls_visible is True

    scene.handle_event(click(scene.back_rect))
    assert scene.controls_visible is False


def test_menu_exit_requests_quit(scene_context):
    context, _ = scene_context
    scene = MenuScene(context)
    scene.enter()

    scene.handle_event(click(scene.exit_rect))

    assert scene.take_transition().target is SceneId.QUIT


def test_selection_keeps_original_defaults_and_wraparound(scene_context):
    context, _ = scene_context
    scene = SelectionScene(context)
    scene.enter()

    assert scene.selected_fighter_1 == 0
    assert scene.selected_fighter_2 == 3

    scene.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_w}))
    scene.handle_event(
        pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN})
    )

    assert scene.selected_fighter_1 == 3
    assert scene.selected_fighter_2 == 0


def test_selection_enter_passes_both_fighters_to_battle(scene_context):
    context, _ = scene_context
    scene = SelectionScene(context)
    scene.enter()

    scene.handle_event(
        pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
    )
    transition = scene.take_transition()

    assert transition.target is SceneId.BATTLE
    assert transition.payload == (FIGHTERS[0], FIGHTERS[3])


def test_selection_back_returns_to_menu(scene_context):
    context, _ = scene_context
    scene = SelectionScene(context)
    scene.enter()

    scene.handle_event(click(scene.back_rect))

    assert scene.take_transition().target is SceneId.MENU


def test_match_victory_wait_is_non_blocking_and_returns_to_menu(scene_context):
    context, fake_time = scene_context
    fake_time.current = 0
    scene = BattleScene(context)
    scene.enter((FIGHTERS[0], FIGHTERS[3]))
    scene.score = [2, 0]
    scene.fighter_2.health = 0

    scene.update(16)

    assert scene.match_over is True
    assert scene.take_transition() is None

    fake_time.current = 1999
    scene.update(16)
    assert scene.take_transition() is None

    fake_time.current = 2000
    scene.update(16)
    assert scene.take_transition().target is SceneId.MENU


def test_non_final_round_recreates_fresh_players_after_result(scene_context):
    context, fake_time = scene_context
    fake_time.current = 0
    scene = BattleScene(context)
    scene.enter((FIGHTERS[0], FIGHTERS[3]))
    original_player = scene.fighter_1
    scene.fighter_2.health = 0

    scene.update(16)
    assert scene.score == [1, 0]

    fake_time.current = 2000
    scene.update(16)

    assert scene.fighter_1 is not original_player
    assert scene.fighter_1.health == 100
    assert scene.fighter_1.energy == 10
    assert scene.round_over is False
