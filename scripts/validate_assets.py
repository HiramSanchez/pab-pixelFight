import ast
from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_FILE = PROJECT_ROOT / "src" / "pixel_fight" / "settings.py"

REQUIRED_ASSETS = (
    "assets/fonts/HelvetiPixel.ttf",
    "assets/fonts/PixelTimesNewRoman.ttf",
    "assets/images/backgrounds/battleground.png",
    "assets/images/backgrounds/controls.png",
    "assets/images/backgrounds/scrolling.png",
    "assets/images/backgrounds/start.png",
    "assets/images/icons/skull.png",
)


def load_fighter_configuration():
    tree = ast.parse(
        SETTINGS_FILE.read_text(encoding="utf-8"),
        filename=str(SETTINGS_FILE),
    )
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "FIGHTERS"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(
        "The FIGHTERS configuration was not found in pixel_fight/settings.py"
    )


def validate_file(relative_path):
    path = PROJECT_ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"Missing required asset: {relative_path}")
    validate_exact_case(path)


def validate_exact_case(path):
    current = PROJECT_ROOT
    for part in path.relative_to(PROJECT_ROOT).parts:
        if part not in {child.name for child in current.iterdir()}:
            raise AssertionError(f"Asset path has incorrect letter case: {path}")
        current /= part


def validate_fighter(fighter):
    fighter_dir = PROJECT_ROOT / "assets" / "images" / "fighters" / fighter["asset_dir"]
    pick_path = fighter_dir / "pick.png"
    spritesheet_path = fighter_dir / "spritesheet.png"

    if not pick_path.is_file():
        raise AssertionError(f"Missing fighter portrait: {pick_path}")
    if not spritesheet_path.is_file():
        raise AssertionError(f"Missing fighter spritesheet: {spritesheet_path}")
    validate_exact_case(pick_path)
    validate_exact_case(spritesheet_path)

    spritesheet = pygame.image.load(str(spritesheet_path))
    size = fighter["size"]
    steps = fighter["animation_steps"]
    rows = spritesheet.get_height() // size
    columns = spritesheet.get_width() // size

    if len(steps) != 10:
        raise AssertionError(f"{fighter['name']} must configure exactly 10 animation rows")
    if spritesheet.get_height() % size or spritesheet.get_width() % size:
        raise AssertionError(f"{fighter['name']} spritesheet is not aligned to {size}px cells")
    if rows < len(steps):
        raise AssertionError(f"{fighter['name']} spritesheet has {rows} rows, needs {len(steps)}")
    if columns < max(steps):
        raise AssertionError(
            f"{fighter['name']} spritesheet has {columns} columns, needs {max(steps)}"
        )


def main():
    for relative_path in REQUIRED_ASSETS:
        validate_file(relative_path)
    for fighter in load_fighter_configuration():
        validate_fighter(fighter)
    print("Asset validation: PASS")


if __name__ == "__main__":
    main()
