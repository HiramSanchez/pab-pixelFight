# Pixel Fight — Agent Guide

## Project overview

Pixel Fight is a small local two-player 2D fighting game with a retro pixel-art
style. The project is intended to remain easy to understand while it is made
more reliable, portable, and extensible in small steps.

- Runtime: Python 3.13 and Pygame 2.6.1.
- Entry point: `main.py` (the repository currently has no `src/` directory).
- Fighter model: `player.py`.
- Runtime resources: `assets/images/` and `assets/fonts/`.
- Current design: module-level Pygame setup, nested blocking loops, shared
  mutable match state in `main.py`, and a small cached resource boundary.

## Current architecture

### Screen and match flow

1. Importing `main.py` initializes Pygame, creates a 1000×600 display, and asks
   `AssetManager` for common images and fonts.
2. `initial_screen()` owns the menu loop. Controls are an overlay inside that
   same loop.
3. `character_selection_screen()` owns the selector loop and returns two
   character dictionaries, or `(None, None)` to return to the menu.
4. `create_fighters()` reuses cached, scaled animation lists and creates two
   `Player` instances.
5. The battle loop in the `if __name__ == "__main__"` block owns the HUD,
   countdown, timer, status-effect processing/rendering, round recreation,
   victory display, and events. It delegates round outcome and score rules to
   `round_rules.py`.
6. A completed best-of-five match returns to the main menu.

There is no scene manager. Menu, selection, and battle are nested `while`
loops. Only the outermost loop coordinates transitions.

### Module responsibilities and data flow

`main.py` currently handles application startup, display and fonts, character
configuration, all scenes, selection previews, asset paths, match creation,
round timing/scoring, HUD, burn ticking, freeze/burn overlays, and shutdown.

`player.py` defines `Player`: sprite slicing, animation selection, input
polling, movement/gravity, blocking, attack hitboxes and immediate damage,
energy, dash, freeze timing, and most combat flags. Burn is stored on `Player`
but advanced by `main.py`.

`round_rules.py` is deliberately independent from Pygame. It resolves KO,
timeout, draws, score deltas, and the first-to-three match threshold. It does
not own timers, rendering, Player mutation, or scenes.

`asset_manager.py` resolves resources from the repository-local `assets/`
directory, never from process CWD. It caches images, fonts, selector idle
frames, and scaled battle animations. Fixed background/skull transforms are
created once during display setup.

Character dictionaries and loaded spritesheets flow from `main.py` into each
`Player`. Every frame, `main.py` passes the opponent and the global
`round_over` flag to `Player.move()`. Players directly mutate the opponent's
health/status and their own energy; `main.py` reads those fields to render and
score the round.

## Gameplay model

### Controls

| Action | Player 1 | Player 2 |
|---|---|---|
| Select previous/next fighter | `W` / `S` | `Up` / `Down` |
| Walk left/right | `A` / `D` | `Left` / `Right` |
| Jump | `W` | `Up` |
| Block (hold) | `1` | `M` |
| Normal attack 1 | `2` | `,` |
| Normal attack 2 | `3` | `.` |
| Special attack | `4` | `/` |
| Start selected match | `Enter` | `Enter` |

Inputs during combat are polled with `pygame.key.get_pressed()`, so attack keys
are hold-driven, not edge-triggered.

### Player state

Important fields are `alive`, `attacking`, `attack_type`, `attack_cooldown`,
`blocking`, `hit`, `jump`, `running`, `dashing`, `frozen`, and `burned`.
These booleans are not a strict finite-state machine and some combinations can
coexist. Animation precedence is: dead → blocking → hit → attacking → jumping
→ running → idle. Freeze bypasses normal animation progression and locks a
frame until its timer expires.

### Animation row indices

Every spritesheet is interpreted as ten horizontal animation rows of 128×128
source cells:

| Index | Action |
|---:|---|
| 0 | Idle |
| 1 | Unused by current state selection (commonly walk in source art) |
| 2 | Running/walking |
| 3 | Jump |
| 4 | Normal attack 1 |
| 5 | Normal attack 2 |
| 6 | Special attack |
| 7 | Block |
| 8 | Hit reaction |
| 9 | Death |

Index 1 is loaded but never selected by the current code.

### Combat rules

- Players start each round with 100 health and 10 energy.
- Normal attack 1 uses a hitbox 1.5 times the shared 80 px body width, deals
  10 damage, and grants 20 energy on an unblocked hit.
- Normal attack 2 uses 1.9 times body width, deals 6 damage, and grants the same
  energy.
- A blocked normal attack deals no damage and grants the attacker 10 energy.
- Damage and effects are resolved when an attack starts, not on an active
  animation frame. Each attack can resolve only once because `attacking`
  prevents a new attack until its animation and cooldown finish.
- The cooldown is 30 calls to `move()`, therefore approximately 0.5 seconds at
  60 FPS rather than a time-based duration.
- Energy is clamped down to 100 in `update()`. Specials require `>= 100` and
  spend 100. Health is clamped to `[0, 100]` across successive updates; energy
  has an upper clamp but no explicit lower clamp.
- Blocking is hold-based and prevents movement, jumping, and attack input.
  There is no chip damage or defender energy gain.
- Both players use the same 80×180 body/hurt rectangle regardless of art.
  Attack rectangles use that body rectangle and current facing.

### Character specials and statuses

- **Raruto:** applies burn on an unblocked special hit. Burn deals 10 damage at
  2, 4, and 6 seconds (30 total); there is no immediate special damage.
- **Starlight:** deals 20 and heals 15 on an unblocked special hit; healing is
  clamped to 100 in the next `update()`.
- **Onichan:** deals 15 and freezes for 3000 ms. Frozen players receive no
  normal input, keep gravity/screen bounds, and have their animation frame
  locked. Freeze timing is owned by `Player.update()`.
- **Bam:** begins a 200 ms dash at 20 px per battle frame and deals 35 only if
  the special's initial hitbox overlaps at activation. Dash motion continues
  outside the normal input gate, including while the round is over or the
  player is frozen.
- Freeze and burn tint generation is owned by `main.py`, rebuilt pixel by pixel
  each frame. An `elif` chain displays only one affected fighter when several
  statuses are active.

### Rounds and match victory

The configured timer is 94 seconds: it includes the three-number countdown and
roughly one second of “FIGHT!”, leaving about 90 seconds of controllable play.
A KO or higher health when time reaches zero awards one point. Equal health at
timeout and simultaneous KO are draws: they award no point and display “No One
wins”. Burn is ticked before the single round resolution step, so lethal burn
ends the round in that frame. After a two-second result period, both `Player`
instances are recreated and all countdown/banner timestamps are reset. First to
three round wins displays victory for two seconds and returns to the main menu.

## Character configuration

Each dictionary in `main.py:fighters` contains:

- `name`: display name.
- `asset_dir`: exact case-sensitive runtime folder component.
- `size`: source cell width/height in pixels; currently 128 for all fighters.
- `scale`: render scale applied to every extracted cell.
- `offset`: scaled sprite displacement from the shared body rectangle.
- `freeze_offset`: unscaled screen displacement used only for the tint overlay.
- `animation_steps`: frame count for rows 0 through 9 in the index table above.

| Character | `asset_dir` | `size` | `scale` | `offset` | `freeze_offset` | `animation_steps` |
|---|---|---:|---:|---|---|---|
| Raruto | `Raruto` | 128 | 1.6 | `[34, 15]` | `[-55, -23]` | `[6, 8, 8, 10, 3, 4, 4, 2, 3, 4]` |
| Starlight | `Starlight` | 128 | 2.1 | `[45, 41]` | `[-95, -87]` | `[7, 7, 8, 8, 4, 10, 10, 7, 3, 6]` |
| Onichan | `onichan` | 128 | 2.0 | `[44, 38]` | `[-88, -75]` | `[5, 6, 7, 8, 4, 4, 4, 4, 3, 6]` |
| Bam | `bam` | 128 | 1.8 | `[40, 27]` | `[-73, -50]` | `[6, 8, 8, 12, 6, 4, 3, 2, 2, 4]` |

## Asset conventions

```text
assets/
├── fonts/
│   ├── HelvetiPixel.ttf
│   └── PixelTimesNewRoman.ttf
└── images/
    ├── backgrounds/{battleground,controls,scrolling,start}.png
    ├── fighters/<fighter>/{pick,spritesheet}.png
    ├── icons/skull.png
    └── ss/*.png
```

- Runtime paths use `pathlib`, are anchored to the source repository, and are
  independent of the current working directory.
- Each `pick.png` is 129×129.
- Each spritesheet uses 128×128 cells, ten rows, and enough columns for the
  largest configured row: Raruto 10×10 cells, Starlight 10×10, Onichan 8×10,
  and Bam 12×10.
- `battleground.png` is exactly 1000×600. `scrolling.png` is 2000×601 and is
  tiled horizontally. `controls.png` is 900×500. `start.png` is loaded but its
  only drawing mode is not used by the current flow.
- `assets/images/ss/` contains README screenshots, not runtime assets.
- Do not infer asset licensing beyond the README links: no license files or
  per-asset attribution records are present in the repository.

## Known issues

The prioritized evidence and remediation details live in
`docs/TECHNICAL_AUDIT.md`.

### Functional bugs

- Bam's dash can move while frozen or after round end and only hits at startup.
- Importing `main` shuts down Pygame because final `pygame.quit()` is outside
  the main guard.

### Performance

- Freeze/burn masks and tint surfaces are rebuilt with nested per-pixel loops.

### Architecture and maintainability

- Global setup/state, nested loops, and scene rendering are concentrated in
  `main.py`; burn behavior is split between modules.
- Player 1/2 input branches and status branches duplicate logic.
- Combat state is a set of overlapping booleans, not an enforced state model.
- Test coverage currently focuses on round rules and fresh Player state; most
  Pygame-coupled behavior still has no automated coverage.

### Portability

- Display and asset loading occur at import time.

### Optional gameplay improvements (not confirmed bugs)

- Character-specific hurtboxes/attack data, frame-based active hits, collision
  between fighters, pause/rematch navigation, audio, and configurable controls.
- Decide explicit policies for timeout ties and simultaneous KO before changing
  them.

## Development rules

1. Do not change existing behavior without documenting the intended change.
2. Keep the game executable after every phase.
3. Avoid mass refactors in one change; migrate one responsibility at a time.
4. Separate bug fixes, refactors, and features into independently verifiable
   changes.
5. Prefer small changes with a focused acceptance check.
6. Preserve Python 3.13 and Pygame 2.6.1 compatibility unless a new decision is
   recorded.
7. Do not rename or move assets without updating every reference and validating
   on a case-sensitive filesystem.
8. Do not replace art, fonts, screenshots, or other resources without
   authorization.
9. Add no framework or dependency unless it solves a demonstrated need.
10. Keep architecture proportional to a small local game; do not add enterprise
    patterns or abstractions with only one use.
11. Add tests for combat, scoring, timers, and state logic that can run without
    opening a graphical window.
12. Record important architecture decisions in `docs/` and keep
    `docs/CURRENT_STATE.md` aligned with behavior.

## Validation commands

Run commands from the repository root.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m py_compile main.py player.py round_rules.py asset_manager.py scripts/validate_assets.py scripts/smoke_test.py
python -m pytest
python scripts/validate_assets.py
python scripts/smoke_test.py
python main.py
```

The smoke test uses SDL's dummy video/audio drivers and validates startup and
Quit handling without opening a visible window. It does not replace a manual
visual/input check.
