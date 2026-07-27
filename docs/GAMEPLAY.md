# Gameplay and Runtime Behavior

This document records the current game and runtime behavior. It describes what
the code does rather than a desired future design. Remaining work is tracked in
`PENDING_WORK.md`.

## Repository and runtime baseline

- Runtime code lives under the installable `src/pixel_fight/` package.
- `pixel_fight.scenes` contains the minimal transition contract plus menu,
  selection, and battle scenes.
- Combat rules/effects live in `pixel_fight.combat`, Player in
  `pixel_fight.entities`, and resource loading in `pixel_fight.resources`.
- `pyproject.toml` owns runtime, development, build, entry-point, package, and
  pytest configuration.
- Python 3.13.0 and Pygame 2.6.1 are the documented and locally validated
  versions.
- The window is fixed at 1000×600 and the target loop rate is 60 FPS.
- Asset loading is anchored to the repository-local `assets/` directory and is
  independent of launch CWD. Frozen builds use PyInstaller's bundle root.

## Distribution state

`VERSION` and `CHANGELOG.md` establish the first packaged preview at 0.1.0.
`packaging/windows/PixelFight.spec` produces a Windows x64 onedir bundle containing the
executable, assets, fonts, README, changelog, and third-party notices.
`scripts/build_windows.ps1` audits packaged assets by SHA-256, performs a
dummy-SDL executable startup check, and creates
`dist/PixelFight-windows-x64.zip`. A GitHub Actions workflow repeats this on
manual dispatch or version tags and uploads a workflow artifact.

Windows is the only packaged target. A visible clean-machine pass remains
manual. Public release is blocked because most art and HelvetiPixel lack exact
file-level provenance, and the project source has no chosen license.

## Complete application flow

```mermaid
flowchart TD
    A[Execute python -m pixel_fight] --> B[Game initializes Pygame, display, context, scenes]
    B --> C[MenuScene]
    C -->|Controls| D[Controls overlay in MenuScene]
    D -->|Back| C
    C -->|Exit / window close| X[pygame.quit + SystemExit]
    C -->|Play transition| E[SelectionScene]
    E -->|Back transition| C
    E -->|Enter + fighter payload| F[BattleScene creates match]
    F --> G[BattleScene update/draw]
    G -->|Round winner below 3 points| H[Result for 2 seconds]
    H --> I[Recreate both Players]
    I --> G
    G -->|First player reaches 3| J[Victory for 2 seconds]
    J --> C
    G -->|Window close| X
    B --> K[One clock, event pump, display update]
```

### Startup

`pixel_fight.__main__` only defines/calls `main()`. Constructing `Game`
initializes Pygame, opens the fixed 1000×600 display, creates the
clock/context/scenes, and enters MenuScene. Importing the entry module does not
initialize Pygame. `Game.run()` guarantees `pygame.quit()` in `finally`.

### Main menu and controls

`MenuScene` uses cached `scrolling.png` and `controls.png`, scrolls two copies of
the background by 0.2 px per frame, and draws Play, Controls, and Exit
rectangles. Mouse clicks still operate them; `Up/Down` or `W/S` moves the
highlight and Enter activates it. Escape requests Quit. Enter or Escape closes
the controls overlay.

Controls remains an overlay rather than a separate scene. While it is open,
underlying buttons remain drawn and their click handlers remain active,
preserving baseline behavior. Play requests SelectionScene; Exit requests the
global Quit transition.

### Character selector

Selection starts with Raruto for Player 1 and Bam for Player 2. `W/S` and
Up/Down wrap through the four-item list. Both may select the same fighter. The
central list outlines each player's choice; a shared choice alternates color
using wall-clock `time.time()`.

When the selector is entered, all four portraits and idle-frame lists are
requested once from `AssetManager`. Each selector frame then:

1. scrolls and draws the background;
2. renders labels and choices;
3. retrieves both portraits and idle-frame lists from in-memory caches;
4. advances one shared preview frame index about every 100 ms;
5. handles keyboard/mouse events.

Enter requests BattleScene with the two shared configuration dictionaries as
payload. Back or Escape explicitly requests MenuScene. Entering either scene
resets its local UI/match state.

## Match lifecycle

```mermaid
stateDiagram-v2
    [*] --> Countdown: create players / score=[0,0]
    Countdown --> FightBanner: 3, 2, 1
    FightBanner --> Combat: about 1 second
    Combat --> RoundResult: KO or timer=0
    RoundResult --> Countdown: score below 3 / recreate players
    RoundResult --> MatchVictory: score equals 3
    MatchVictory --> [*]: return to main menu
```

### Creation and round reset

BattleScene entry resets `score` to `[0, 0]`, obtains cached animations, and
calls `reset_round()`, which constructs Players at `(200, 310)` and
`(700, 310)`. Player 2 starts flipped.

`reset_round()` resets `round_start_time`, `round_over`, `intro_count`,
`fight_displayed`, `fight_display_start`, `last_count_update`,
`round_over_time`, and `winner_name`. Match setup and every later round use
this function. Between rounds both Players are reconstructed from already-loaded
sheets, resetting health, energy, movement, combat, freeze, burn, dash, and
animation fields.

### Countdown, banner, and timer

`ROUND_TIME_LIMIT` is 94,000 ms. The timer starts before the three-second
countdown. After 3 reaches 0, “FIGHT!” appears for about one second. Movement is
enabled afterward, so controllable combat lasts approximately 90 seconds. The
timer is hidden until it reaches 91 seconds and displays truncated integers.
Fighters still run `update()` and draw during the intro, but `move()` is not
called.

### Per-frame combat order

The single Game loop obtains events and delta time once. BattleScene then:

1. caps frame rate;
2. calculates time remaining;
3. draws scaled background and HUD;
4. draws countdown/banner or, while time remains, calls `move()` for Player 1
   then Player 2;
5. updates each Player's effects, animations, and death state, then draws both;
6. resolves KO/timeout/draw once and applies its score delta;
7. handles result/victory and possibly recreates players;
8. draws cached overlays for all active burn/freeze effects;
9. returns control to Game, which performs the only display update.

The ordering matters: Player-owned burn damage is applied before the outcome
resolver, so a lethal tick ends the round in the same frame. Player 1
movement/attack is still processed before Player 2, which can affect same-frame
interactions.

### Pause and match navigation

Escape or `P` opens a battle overlay and suspends scene updates. On resume, all
round, animation, blink, burn, freeze, and dash timestamps are shifted by the
paused duration, so no gameplay time elapses while paused. From the overlay,
Escape/`P` resumes, `R` starts a fresh zero-score match with the same fighters,
`S` returns to character selection, and `M` returns to the main menu. Restart
recreates both Players and resets every round timer/status.

### KO, timeout, scoring, and victory

- If time expires, higher health receives one score point. Equal health sets
  `winner_name = "No One"` and awards no point.
- A single pure resolver in `pixel_fight.combat.round_rules` handles both KO
  and timeout.
  Simultaneous KO is a draw and awards no point.
- During `round_over`, the winner text is shown while Player animations/status
  processing continue.
- Below three points, two seconds after `round_over_time`, both Players are
  recreated and countdown starts again.
- At exactly three points, victory text remains visible for two seconds through
  a non-blocking timer; window-close events continue to work.
- When that timer ends, BattleScene requests MenuScene. There is no direct
  rematch or selector transition.

## Player behavior

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running: horizontal key
    Idle --> Jump: jump key and grounded
    Idle --> Blocking: block held
    Idle --> Attacking: attack accepted
    Running --> Idle: key released
    Jump --> Idle: ground contact
    Blocking --> Idle: block released
    Attacking --> Idle: animation ends
    Idle --> Hit: unblocked hit
    Attacking --> Hit: opponent hit mutates flag
    Hit --> Idle: hit animation ends
    state Frozen {
      [*] --> FrameLocked
    }
    Idle --> Frozen: Onichan special
    Running --> Frozen: Onichan special
    Hit --> Frozen: Onichan special
    Frozen --> Idle: 3000 ms elapsed
    Idle --> Dead: health <= 0
    Hit --> Dead: health <= 0
    Dead --> Dead: last death frame
```

This diagram is approximate because booleans can overlap. `dashing` and
`burned` are orthogonal flags; freeze can coexist with them. Animation action
priority and freeze's early return determine what is visible.

### Movement and facing

`move()` polls the entire keyboard state, then delegates in fixed order to
configured input, dash, gravity, bounds, facing, cooldown, and position
updates. Normal input is permitted only when not attacking, alive, round active,
and not frozen. `ControlScheme` mappings remove separate P1/P2 branches while
preserving the original keys. Walk speed is 10 px per battle frame, gravity is
2 velocity units per frame, and jump velocity begins at -30. The floor is
`screen_height - 110`; only horizontal screen edges and the floor are enforced.
There is no ceiling, player-player collision, knockback, or stage geometry.
Facing is recalculated from opponent center positions after movement.

### Attacks and collision

Each fighter explicitly configures an 80×180 hurtbox, preserving the previous
geometry independently of sprite scale. Every move has an immutable
`AttackDefinition` with damage, energy rules, width, animation row, and
startup/active/recovery frames. Attack rectangles extend from the attacker's
center in the facing direction and retain the hurtbox height. Collision,
damage, and effects resolve only during active frames, with one result allowed
per activation. The compatibility `surface` arguments are unused; debug hitbox
drawing is absent.

Attack input is disabled while `attacking`; when the selected attack animation
ends, a 30-frame cooldown begins. If a key remains held, the attack will fire
again when the cooldown reaches zero. Cooldown decrements only when `move()` is
called, so it pauses during countdown/result and stretches when FPS falls.

Animation selection, frame advancement, freeze locking, and animation-end
cleanup are separate methods. Named constants map directly to the ten existing
spritesheet rows; priority and 50 ms frame timing are unchanged.

### Health, energy, block

Health and energy start at 100 and 10. Normal attacks give the attacker 20
energy for an unblocked hit or 10 when blocked. Energy above 100 is clamped on
the next `update()`. Health above 100 is likewise clamped. Health at or below
zero is set to zero and marks the player dead.

Block is a held state. It cancels input inside its branch but does not have a
time limit. Because block is only refreshed inside the normal-input gate, the
flag may remain true while an incompatible gate such as freeze or round-over is
active.

### Freeze, burn, and dash

Onichan starts or refreshes the target's 3000 ms `TimedEffect`.
`Player.update()` owns expiry and freezes the current frame (or the final hit
frame).

Raruto starts or refreshes the target's `BurnEffect`. Player applies every tick
due at 2, 4, and 6 seconds, including multiple overdue ticks after a slow frame.
It applies no damage after round end.

Bam starts a 200 ms `TimedEffect`, spends energy, and carries a
3.25-hurtbox-width attack during the dash. Movement uses 1200 px/s and frame
delta, preserving 20 px/frame at 60 FPS. The first overlap during travel deals
35 damage, and one-hit tracking prevents repeats. Freeze, death, and round end
cancel travel.

Burn and freeze are orthogonal and may coexist. The battle renderer loops over
both players, drawing burn first and freeze second. `AssetManager` caches mask
surfaces by source frame, tint color, and flip direction.

The HUD displays `BURN` and `FROZEN` labels for active effects, in addition to
the existing blinking `MAX` energy feedback.

## Animation and asset management

`AssetManager.fighter_animations()` slices and scales one cached animation list
per character configuration. New rounds share these immutable surfaces between
new Player instances. The selector has a separate cached, unscaled idle list so
its baseline preview size remains unchanged. `Player.load_images()` remains as
a compatibility fallback for direct construction and tests. Battle animation
advances at 50 ms per frame using elapsed milliseconds; it advances at most one
frame per call and does not carry extra elapsed time.

The first request for a source frame/color/orientation creates a mask overlay;
`AssetManager` reuses it afterward. The configured `freeze_offset` is separate
from the normal scaled sprite offset, which makes alignment character-specific
and fragile.

## Automated verification

Pytest runs 113 deterministic tests without opening a visible game window.
Shared test builders create lightweight Players with in-memory animation
surfaces, and a pressed-key adapter exercises both control schemes. Coverage
includes assets/caching, round resolution and complete reset state, scene
transitions, Player defaults and animation priority, stat bounds, attack
acceptance and cleanup, every configured combat move, and timed freeze, burn,
and dash behavior. `scripts/smoke_test.py` remains a separate SDL-dummy startup
and Quit check rather than part of the unit suite.
