from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_ASSET_ROOT = PROJECT_ROOT / "assets"


class AssetManager:
    def __init__(self, asset_root=DEFAULT_ASSET_ROOT):
        self.asset_root = Path(asset_root).resolve()
        self._images = {}
        self._fonts = {}
        self._idle_frames = {}
        self._fighter_animations = {}
        self._status_overlays = {}

    def path(self, relative_path):
        path = (self.asset_root / relative_path).resolve()
        if not path.is_relative_to(self.asset_root):
            raise ValueError(f"Asset path escapes the asset root: {relative_path}")
        return path

    def image(self, relative_path, alpha=True):
        path = self.path(relative_path)
        cache_key = (path, alpha)
        if cache_key not in self._images:
            image = pygame.image.load(path)
            self._images[cache_key] = image.convert_alpha() if alpha else image.convert()
        return self._images[cache_key]

    def font(self, relative_path, size):
        path = self.path(relative_path)
        cache_key = (path, size)
        if cache_key not in self._fonts:
            self._fonts[cache_key] = pygame.font.Font(path, size)
        return self._fonts[cache_key]

    def fighter_image(self, fighter, filename):
        relative_path = Path("images") / "fighters" / fighter["asset_dir"] / filename
        return self.image(relative_path)

    def idle_frames(self, fighter):
        cache_key = (
            fighter["asset_dir"],
            fighter["size"],
            fighter["animation_steps"][0],
        )
        if cache_key not in self._idle_frames:
            spritesheet = self.fighter_image(fighter, "spritesheet.png")
            size = fighter["size"]
            self._idle_frames[cache_key] = tuple(
                spritesheet.subsurface(pygame.Rect(index * size, 0, size, size))
                for index in range(fighter["animation_steps"][0])
            )
        return self._idle_frames[cache_key]

    def fighter_animations(self, fighter):
        cache_key = (
            fighter["asset_dir"],
            fighter["size"],
            fighter["scale"],
            tuple(fighter["animation_steps"]),
        )
        if cache_key not in self._fighter_animations:
            spritesheet = self.fighter_image(fighter, "spritesheet.png")
            size = fighter["size"]
            scaled_size = (size * fighter["scale"], size * fighter["scale"])
            self._fighter_animations[cache_key] = [
                [
                    pygame.transform.scale(
                        spritesheet.subsurface(
                            frame_index * size,
                            action_index * size,
                            size,
                            size,
                        ),
                        scaled_size,
                    )
                    for frame_index in range(frame_count)
                ]
                for action_index, frame_count in enumerate(fighter["animation_steps"])
            ]
        return self._fighter_animations[cache_key]

    def status_overlay(self, image, color, flipped=False):
        cache_key = (id(image), tuple(color), flipped)
        if cache_key not in self._status_overlays:
            overlay = pygame.mask.from_surface(image).to_surface(
                setcolor=color,
                unsetcolor=(0, 0, 0, 0),
            )
            if flipped:
                overlay = pygame.transform.flip(overlay, True, False)
            self._status_overlays[cache_key] = overlay
        return self._status_overlays[cache_key]
