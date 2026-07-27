import os
from pathlib import Path
import subprocess
import sys

import pygame
import pytest

from pixel_fight.game import GameContext
from pixel_fight.resources.asset_manager import AssetManager
from pixel_fight.scenes import SceneId
from pixel_fight.scenes.battle import BattleScene
from pixel_fight.scenes.menu import MenuScene
from pixel_fight.scenes.selection import SelectionScene
from pixel_fight.settings import FIGHTERS


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


def keydown(key):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key})


def test_importing_main_has_no_pygame_initialization_side_effect():
    environment = os.environ.copy()
    environment["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    environment["PYTHONPATH"] = str(Path.cwd() / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import pygame; "
                "assert not pygame.get_init(); "
                "import pixel_fight.__main__; "
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


def test_menu_keyboard_navigates_and_activates_buttons(scene_context):
    context, _ = scene_context
    scene = MenuScene(context)
    scene.enter()

    scene.handle_event(keydown(pygame.K_DOWN))
    assert scene.selected_button == 1
    scene.handle_event(keydown(pygame.K_RETURN))
    assert scene.controls_visible is True

    scene.handle_event(keydown(pygame.K_ESCAPE))
    assert scene.controls_visible is False
    scene.handle_event(keydown(pygame.K_UP))
    scene.handle_event(keydown(pygame.K_RETURN))
    assert scene.take_transition().target is SceneId.SELECTION


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


def test_selection_escape_returns_to_menu(scene_context):
    context, _ = scene_context
    scene = SelectionScene(context)
    scene.enter()

    scene.handle_event(keydown(pygame.K_ESCAPE))

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


def test_reset_round_restores_all_round_timing_fields(scene_context):
    context, fake_time = scene_context
    fake_time.current = 4321
    scene = BattleScene(context)
    scene.enter((FIGHTERS[0], FIGHTERS[3]))
    scene.round_over = True
    scene.intro_count = 0
    scene.fight_displayed = True
    scene.fight_display_start = 100
    scene.last_count_update = 200
    scene.round_over_time = 300
    scene.winner_name = "Raruto"

    scene.reset_round()

    assert scene.round_start_time == 4321
    assert scene.round_over is False
    assert scene.intro_count == 3
    assert scene.fight_displayed is False
    assert scene.fight_display_start == 0
    assert scene.last_count_update == 4321
    assert scene.round_over_time == 0
    assert scene.winner_name is None


def test_pause_freezes_match_and_resume_preserves_elapsed_time(scene_context):
    context, fake_time = scene_context
    fake_time.current = 1000
    scene = BattleScene(context)
    scene.enter((FIGHTERS[0], FIGHTERS[3]))
    scene.fighter_1.apply_burn(1000)
    original_health = scene.fighter_1.health

    scene.handle_event(keydown(pygame.K_ESCAPE))
    fake_time.current = 6000
    scene.update(16)

    assert scene.paused is True
    assert scene.fighter_1.health == original_health

    scene.handle_event(keydown(pygame.K_p))
    scene.update(16)

    assert scene.paused is False
    assert scene.round_start_time == 6000
    assert scene.fighter_1.burn_effect.started_at == 6000
    assert scene.fighter_1.health == original_health


@pytest.mark.parametrize(
    ("key", "target"),
    [(pygame.K_s, SceneId.SELECTION), (pygame.K_m, SceneId.MENU)],
)
def test_pause_navigation_requests_expected_scene(scene_context, key, target):
    context, fake_time = scene_context
    fake_time.current = 0
    scene = BattleScene(context)
    scene.enter((FIGHTERS[0], FIGHTERS[3]))
    scene.handle_event(keydown(pygame.K_ESCAPE))

    scene.handle_event(keydown(key))

    assert scene.take_transition().target is target


def test_pause_restart_starts_fresh_match_with_same_fighters(scene_context):
    context, fake_time = scene_context
    fake_time.current = 2500
    scene = BattleScene(context)
    scene.enter((FIGHTERS[0], FIGHTERS[3]))
    scene.score = [2, 1]
    scene.fighter_1.health = 5
    old_fighter = scene.fighter_1
    scene.handle_event(keydown(pygame.K_ESCAPE))

    scene.handle_event(keydown(pygame.K_r))

    assert scene.paused is False
    assert scene.score == [0, 0]
    assert scene.fighter_1 is not old_fighter
    assert scene.fighter_1.health == 100
    assert scene.fighter_1_data is FIGHTERS[0]
    assert scene.fighter_2_data is FIGHTERS[3]


def test_status_indicators_show_active_effects(
    scene_context,
    monkeypatch,
):
    context, fake_time = scene_context
    fake_time.current = 0
    scene = BattleScene(context)
    scene.enter((FIGHTERS[0], FIGHTERS[3]))
    scene.fighter_1.apply_burn(0)
    scene.fighter_1.apply_freeze(0)
    labels = []
    monkeypatch.setattr(
        context,
        "draw_text",
        lambda text, *args: labels.append(text),
    )

    scene.draw_state_indicators(scene.fighter_1, 120)

    assert labels == ["BURN", "FROZEN"]
