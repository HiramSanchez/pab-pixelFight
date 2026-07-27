# Improvement Roadmap

The phases below are deliberately incremental. Each phase should be delivered
as one or more small changes; acceptance means the game remains runnable and
behavior changes are documented.

## Phase 0 — Baseline and safety

**Status: completed locally (2026-07-26).** Requirements, compilation, 15
focused tests, asset/spritesheet validation, and a headless startup/Quit smoke
test are repeatable. A case-sensitive CI runner remains pending because the
known path/case defects belong to Phase 2.

- **Objective:** Make setup and baseline verification repeatable without
  changing gameplay.
- **Files:** `requirements.txt`, README, `docs/`, then small smoke-test helpers.
- **Expected changes:** Pin Pygame 2.6.1; preserve this audit; add an asset
  inventory/check and a headless startup check; record known behavior.
- **Acceptance:** Clean install on Python 3.13; Python files compile; every
  configured asset exists and every animation row fits; headless menu can
  initialize and handle Quit.
- **Tests:** `py_compile`, asset-dimension validation, controlled dummy-video
  startup on Windows and one case-sensitive OS/CI job.
- **Risks:** Headless SDL differs from a real display/audio environment.
- **Dependencies:** None.
- **Size:** Small.

## Phase 1 — Functional corrections

**Status: completed (2026-07-26).** Round resolution is centralized and tested;
simultaneous KO and timeout ties are explicit no-score draws; score is applied
once; lethal burn resolves in the same frame; and round timing/Player state is
reset consistently. Victory intentionally continues returning to the menu.

- **Objective:** Make round/match outcomes deterministic before structural work.
- **Files:** `main.py`, new focused tests, possibly a small `round_rules.py`.
- **Expected changes:** One round resolver; explicit simultaneous-KO and timeout
  tie policy; consistent score update; safe reset of timers/statuses; document
  whether victory returns to menu or selector.
- **Acceptance:** Exactly one result per round; P1/P2 are symmetric; score never
  increments twice; best-of-five ends at three; all round state resets.
- **Tests:** KO each side, simultaneous KO, health comparisons at timeout, tie,
  lethal burn ordering, three-win match, fresh-round fields.
- **Risks:** Tie and simultaneous-KO handling require a product decision and
  alter visible gameplay.
- **Dependencies:** Phase 0 baseline.
- **Size:** Medium.

## Phase 2 — Portability and resource loading

- **Objective:** Launch reliably from any working directory and remove repeated
  loading.
- **Files:** `main.py`, fighter config, new `src/resources/asset_manager.py` only
  when package migration begins, asset folder names if approved.
- **Expected changes:** `pathlib` root anchored at source location; explicit
  asset folder key; case-correct paths; cache backgrounds, portraits,
  spritesheets, frames, and transformed skull/background.
- **Acceptance:** Start from repository root and parent directory on Windows and
  a case-sensitive OS; selector performs no disk loads after scene entry;
  visuals match baseline.
- **Tests:** Asset path tests, load-count instrumentation, manual menu/selector/
  battle visual pass.
- **Risks:** Case-only Git renames and packaged-resource paths.
- **Dependencies:** Phase 0; coordinate with future package layout.
- **Size:** Medium.

## Phase 3 — States and effects

- **Objective:** Give freeze, burn, and dash one clear update/render owner and
  stable timing.
- **Files:** `player.py`, battle loop, optionally
  `combat/status_effect.py`.
- **Expected changes:** Timed-effect records; explicit coexistence/precedence;
  centralized burn ticks; cached/blended overlays; dash cancellation rules;
  elapsed-time cooldowns/physics migration where safely characterized.
- **Acceptance:** Both players can display effects simultaneously; freeze lasts
  configured real time; burn applies exactly three ticks under lag; no
  post-round mutation unless intentionally specified; dash respects declared
  freeze/death/result rules.
- **Tests:** Effect duration/ticks, refresh behavior, simultaneous effects,
  lethal burn, dash+freeze, low/variable-FPS simulation.
- **Risks:** Frame ordering and balance are highly coupled.
- **Dependencies:** Phase 1 result resolver and Phase 2 frame cache.
- **Size:** Large.

## Phase 4 — Scene separation

- **Objective:** Replace nested loops with a small, explicit screen flow.
- **Files:** `main.py`, `game.py`, `scenes/menu_scene.py`,
  `scenes/selection_scene.py`, `scenes/battle_scene.py`; optional result state
  within battle before adding a separate file.
- **Expected changes:** One application loop/event pump; scene enter/update/
  render/exit methods; non-blocking victory timer; explicit transition values.
- **Acceptance:** Menu, controls, selector, match, result, Quit, and return paths
  behave as documented; no `pygame.time.wait`; one display update per frame.
- **Tests:** Transition unit tests and manual navigation/close tests at each
  screen.
- **Risks:** A total rewrite can subtly alter timing; migrate one scene at a
  time behind the current entry point.
- **Dependencies:** Phases 1–2; Phase 3 may precede or follow if interfaces stay
  narrow.
- **Size:** Large.

## Phase 5 — Player refactor

- **Objective:** Make Player understandable and configurable without changing
  combat results.
- **Files:** `player.py` → `entities/player.py`, `settings.py`, control/character
  configuration, tests.
- **Expected changes:** Named constants; controls mapping removes P1/P2
  branches; small methods for input, physics, action choice, animation; primary
  action state separated from orthogonal effects.
- **Acceptance:** Identical baseline controls, movement, animation selection,
  damage, and timings for fixed test scenarios; no `player == 1/2` input
  duplication.
- **Tests:** Input mapping, movement bounds, jump/landing, animation priority,
  cooldown, blocked/unblocked attacks.
- **Risks:** State-transition order is easy to change unintentionally.
- **Dependencies:** Prefer Phases 1, 3, and 4 seams first.
- **Size:** Large.

## Phase 6 — Combat model

- **Objective:** Align hits with animation and allow character/move tuning.
- **Files:** `combat/attack.py`, character config, Player/BattleScene, optional
  debug rendering.
- **Expected changes:** Attack definitions with damage, cost, hitbox, startup/
  active/recovery frames; configurable hurtboxes; one-hit tracking; defined
  dash contact; optional knockback/block feedback.
- **Acceptance:** Each activation hits at most once; visible active frame and
  hitbox agree; blocked/unblocked outcomes and energy are deterministic; all
  four characters have explicit data.
- **Tests:** Frame windows, facing hitboxes, miss/hit/block, duplicate
  prevention, boundaries, every special.
- **Risks:** This intentionally changes feel and balance; tune separately from
  infrastructure.
- **Dependencies:** Phases 3 and 5.
- **Size:** Large.

## Phase 7 — Test suite

- **Objective:** Cover game rules broadly without requiring a window.
- **Files:** `tests/`, `pytest.ini` if useful, a separate development
  requirements file, extracted pure logic.
- **Expected changes:** Fixtures/builders and deterministic clock/input
  adapters; coverage for stats, score, rounds, states, attacks, effects.
- **Acceptance:** Tests run headlessly and deterministically on Python 3.13;
  failures identify one rule; graphical smoke test remains separate.
- **Tests:** Health/energy bounds, damage/block, score/ties, round reset,
  animation/action transitions, freeze/burn/dash, attack hit tracking.
- **Risks:** Tests coupled to implementation impede refactor; assert behavior
  and public state transitions.
- **Dependencies:** Begin focused tests in every earlier phase; this phase fills
  remaining gaps.
- **Size:** Medium.

## Phase 8 — User experience

- **Objective:** Improve match control and feedback after core rules stabilize.
- **Files:** scenes, HUD/UI, settings, new authorized audio assets.
- **Expected changes:** Pause, restart/rematch, selector/menu return, keyboard
  menu support, state indicators, clearer victory/result screen, audio.
- **Acceptance:** Players can pause/resume and leave a match safely; all
  transitions reset correct state; visible/audio feedback has controllable
  volume and no missing-asset crash.
- **Tests:** Transition/reset tests plus manual input/audio/display checks.
- **Risks:** Asset licensing and control conflicts; accessibility concerns.
- **Dependencies:** Phase 4 scenes and stable state rules.
- **Size:** Medium.

## Phase 9 — Documentation and distribution

- **Objective:** Make the game installable, attributable, and releasable.
- **Files:** README, licenses/attribution, changelog, build config, screenshots,
  release workflow.
- **Expected changes:** Verified asset provenance/licenses; current captures;
  platform instructions; versioning/changelog policy; executable build (for
  example PyInstaller only if chosen).
- **Acceptance:** Fresh Windows install runs from documented steps; chosen
  additional platform works or is explicitly unsupported; distribution
  includes assets/fonts and license notices.
- **Tests:** Clean-machine/VM build and launch; packaged asset audit; smoke
  navigation and one match.
- **Risks:** Missing historical asset license details and antivirus/build
  behavior.
- **Dependencies:** Stable paths from Phase 2 and architecture from Phase 4.
- **Size:** Medium.

## Recommended immediate next slice

Begin Phase 2 as a separate change: source-root `pathlib` paths, explicit
case-correct asset identifiers, and a selector cache. Add a case-sensitive CI
job once the runtime can pass it. Do not combine those changes with status,
scene, or Player refactors.
