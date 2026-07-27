from pathlib import Path

import pygame
import pytest

from asset_manager import AssetManager, DEFAULT_ASSET_ROOT


ONICHAN = {
    "name": "Onichan",
    "asset_dir": "onichan",
    "size": 128,
    "scale": 2,
    "animation_steps": [5, 6, 7, 8, 4, 4, 4, 4, 3, 6],
}


@pytest.fixture(autouse=True)
def pygame_display():
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def test_default_asset_root_is_anchored_to_project_not_cwd(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    manager = AssetManager()

    assert manager.asset_root == DEFAULT_ASSET_ROOT.resolve()
    assert manager.path("images/icons/skull.png").is_file()


def test_asset_path_cannot_escape_root():
    manager = AssetManager()

    with pytest.raises(ValueError, match="escapes"):
        manager.path(Path("..") / "main.py")


def test_image_is_loaded_only_once(monkeypatch):
    manager = AssetManager()
    original_load = pygame.image.load
    loaded_paths = []

    def counting_load(path):
        loaded_paths.append(Path(path))
        return original_load(path)

    monkeypatch.setattr(pygame.image, "load", counting_load)

    first = manager.image("images/icons/skull.png")
    second = manager.image("images/icons/skull.png")

    assert first is second
    assert loaded_paths == [manager.path("images/icons/skull.png")]


def test_case_correct_fighter_directory_is_used():
    manager = AssetManager()

    path = manager.path(
        Path("images") / "fighters" / ONICHAN["asset_dir"] / "spritesheet.png"
    )

    assert path.parent.name == "onichan"
    assert path.is_file()


def test_idle_and_battle_frames_are_cached():
    manager = AssetManager()

    first_idle = manager.idle_frames(ONICHAN)
    second_idle = manager.idle_frames(ONICHAN)
    first_animations = manager.fighter_animations(ONICHAN)
    second_animations = manager.fighter_animations(ONICHAN)

    assert first_idle is second_idle
    assert first_animations is second_animations
    assert len(first_idle) == ONICHAN["animation_steps"][0]
    assert [len(row) for row in first_animations] == ONICHAN["animation_steps"]
