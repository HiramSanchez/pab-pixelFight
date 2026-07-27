import os
import runpy
import sys
from pathlib import Path


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pygame


def main():
    pygame.init()
    pygame.time.set_timer(pygame.QUIT, 100, loops=1)

    try:
        runpy.run_path(str(PROJECT_ROOT / "main.py"), run_name="__main__")
    except SystemExit as error:
        if error.code not in (None, 0):
            raise

    print("Headless startup: PASS")


if __name__ == "__main__":
    main()
