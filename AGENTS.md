# Pixel Fight — Agent Guide

## Project overview

Pixel Fight is a small local two-player 2D fighting game with a retro pixel-art
style. The project is intended to remain easy to understand while it is made
more reliable, portable, and extensible in small steps.

- Runtime: Python 3.13 and Pygame 2.6.1.
- Entry point: `main.py` (the repository currently has no `src/` directory).
- Fighter model: `player.py`.
- Runtime resources: `assets/images/` and `assets/fonts/`.
- Current design: one `Game` loop, three explicit scenes, Player-owned combat
  state, and cached resource/timed-effect boundaries.

## Current architecture

### Screen and match flow

1. `main.py` calls `Game().run()` and has no import-time Pygame side effects.
2. `Game` initializes/shuts down Pygame and owns the only clock, event pump,
   display update, active scene, and transition processing.
3. `MenuScene` owns mouse/keyboard menu navigation and the controls overlay.
4. `SelectionScene` owns both selections and cached previews; Enter requests
   battle with the two character dictionaries and Back requests menu.
5. `BattleScene` owns match/round state, HUD, countdown, timer, Player creation,
   status rendering, scoring, pause/navigation controls, and a non-blocking
   result timer.
6. A completed best-of-five match explicitly transitions to the main menu.

### Module responsibilities and data flow

`main.py` is only the executable entry point. `game.py` owns application
lifecycle and builds a `GameContext` containing the screen, assets, fonts, and
time source. It coordinates scenes but does not implement gameplay rules.

`settings.py` contains window, color, timing, character constants, and the two
immutable `ControlScheme` mappings.

`scenes/` contains the minimal `Scene` transition contract plus menu,
selection, and battle implementations. Scene fields replace the former
module-level UI/match globals.

`player.py` defines `Player`: sprite slicing, configured input polling,
movement/gravity, blocking, attack activation/resolution, energy, animation
state, and ownership of dash/freeze/burn instances. `combat/attack.py` defines
immutable move data and hitbox/frame-window rules. Movement and animation
orchestration delegate to small methods; no input branch depends on player
number.

`round_rules.py` is deliberately independent from Pygame. It resolves KO,
timeout, draws, score deltas, and the first-to-three match threshold. It does
not own timers, rendering, Player mutation, or scenes.

`asset_manager.py` resolves resources from the repository-local `assets/`
directory, or PyInstaller's bundle root when frozen, never from process CWD. It
caches images, fonts, selector idle frames, scaled battle animations, and
status overlays. Fixed background/skull transforms are created once during
display setup.

`status_effect.py` contains Pygame-independent timed-effect records and the
explicit burn/freeze tint precedence. `TimedEffect` is used for freeze and dash;
`BurnEffect` calculates all due damage ticks from elapsed milliseconds.

`tests/conftest.py` provides lightweight Player construction and simulated
pressed-key input for deterministic rule tests. The pytest suite is headless;
the SDL-dummy startup/Quit check remains a separate script.

Character dictionaries and cached animations flow from `SelectionScene` through
a transition into `BattleScene`, then into each Player. Every combat frame,
BattleScene passes the opponent and its `round_over` state to `Player.move()`.
Players directly mutate opponent health/status and their own energy;
BattleScene reads those fields to render and score.

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

Menu choices use `Up/Down` or `W/S` and `Enter`. `Escape` leaves the selector.
During battle, `Escape` or `P` pauses. The pause overlay supports resume,
restart match (`R`), character selection (`S`), and main menu (`M`).

Inputs during combat are polled with `pygame.key.get_pressed()`, so attack keys
are hold-driven, not edge-triggered. Each Player receives a `ControlScheme`;
the default is selected from `settings.PLAYER_CONTROLS` by player number.

### Player state

Important fields are `alive`, `attacking`, `attack_type`, `attack_cooldown`,
`blocking`, `hit`, `jump`, `running`, plus `dash_effect`, `freeze_effect`, and
`burn_effect`. Read-only compatibility properties expose `dashing`, `frozen`,
`burned`, and `burn_ticks`. Named action/attack constants replace magic row/type
numbers. `select_animation_action()` preserves precedence: dead → blocking →
hit → attacking → jumping → running → idle. Freeze remains orthogonal and
locks a frame until its timer expires.

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
- Each configured attack has startup, active, and recovery frames whose sum
  matches its animation row. Damage and effects resolve only during active
  frames, and one-hit tracking limits each activation to one collision result.
- The cooldown is 30 calls to `move()`, therefore approximately 0.5 seconds at
  60 FPS rather than a time-based duration.
- Energy is clamped down to 100 in `update()`. Specials require `>= 100` and
  spend 100. Health is clamped to `[0, 100]` across successive updates; energy
  has an upper clamp but no explicit lower clamp.
- Blocking is hold-based and prevents movement, jumping, and attack input.
  There is no chip damage or defender energy gain.
- Every fighter explicitly configures an 80×180 hurtbox, preserving the
  baseline geometry while allowing later tuning. Each move configures its own
  attack width; rectangles use the hurtbox height and current facing.

### Character specials and statuses

- **Raruto:** applies burn on an unblocked special hit. Burn deals 10 damage at
  2, 4, and 6 seconds (30 total); delayed frames catch up every due tick and
  reapplying burn restarts the schedule. There is no immediate special damage
  and no burn damage after round end.
- **Starlight:** deals 20 and heals 15 on an unblocked special hit; healing is
  clamped to 100 in the next `update()`.
- **Onichan:** deals 15 and freezes for 3000 ms. Frozen players receive no
  normal input, keep gravity/screen bounds, and have their animation frame
  locked. Reapplying freeze restarts its duration.
- **Bam:** begins a 200 ms dash at 1200 px/s (equivalent to 20 px/frame at
  60 FPS) and deals 35 on the first contact anywhere during travel. Dash
  cancels on freeze, death, or round end.
- Burn and freeze may coexist. Both players render their active effects; burn
  tint is drawn first and freeze tint second. Overlays are cached by animation
  frame, color, and orientation.

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

Each dictionary in `settings.py:FIGHTERS` contains:

- `name`: display name.
- `asset_dir`: exact case-sensitive runtime folder component.
- `size`: source cell width/height in pixels; currently 128 for all fighters.
- `scale`: render scale applied to every extracted cell.
- `offset`: scaled sprite displacement from the shared body rectangle.
- `freeze_offset`: unscaled screen displacement used only for the tint overlay.
- `hurtbox`: collision rectangle width and height.
- `animation_steps`: frame count for rows 0 through 9 in the index table above.

`settings.ATTACK_DEFINITIONS` provides three explicit moves per fighter with
damage, energy cost/reward, hitbox width, animation row, startup/active/recovery
frames, and optional special effect.

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
- `THIRD_PARTY_NOTICES.md` is the authoritative provenance inventory. Do not
  infer licenses for unresolved files; public binary release remains blocked
  until each bundled asset is mapped to an exact source/license.

## Known issues

The prioritized evidence and remediation details live in
`docs/TECHNICAL_AUDIT.md`.

### Functional bugs

- No confirmed functional bug remains from Phases 0–8.

### Performance

- Normal movement, gravity, and attack cooldowns remain frame-based.

### Architecture and maintainability

- Combat state is a set of overlapping booleans, not an enforced state model.
- Player still owns combat resolution and overlapping boolean action states;
  further state-model changes are outside the completed combat-data phase.

### Optional gameplay improvements (not confirmed bugs)

- Fighter-to-fighter body collision, audio, and configurable controls.
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
python -m py_compile main.py game.py settings.py player.py round_rules.py asset_manager.py status_effect.py combat/__init__.py combat/attack.py scenes/base.py scenes/menu_scene.py scenes/selection_scene.py scenes/battle_scene.py scripts/validate_assets.py scripts/validate_distribution.py scripts/smoke_test.py scripts/smoke_test_executable.py
python -m pytest
python scripts/validate_assets.py
python scripts/smoke_test.py
python main.py
```

The smoke test uses SDL's dummy video/audio drivers and validates startup and
Quit handling without opening a visible window. It does not replace a manual
visual/input check. Windows packaging additionally uses
`scripts/build_windows.ps1`; follow `docs/RELEASING.md`.
