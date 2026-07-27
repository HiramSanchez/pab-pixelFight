# Technical Audit

Audit baseline: Python 3.13.0, Pygame 2.6.1, Windows, current repository state.
“Confirmed” means directly observed in code or reproduced. “Risk” means a
credible failure mode needing a targeted test or product decision. Suggested
gameplay changes are labeled optional rather than bugs.

Severity indicates impact on reliability or future change, not effort.

## Prioritized findings

### PF-001 — Case-sensitive fighter paths

- **Category / severity:** Functional bug and portability / high
- **Affected:** `main.py` fighter configuration and all fighter-loading helpers
- **Description:** Display names `Onichan` and `Bam` are used as folder names,
  but tracked folders are `onichan` and `bam`.
- **Impact:** These two characters fail to load on case-sensitive filesystems.
- **Evidence:** `fighters` names at lines 76–77; `git ls-files` confirms
  lowercase directories; paths concatenate `name` at lines 278, 286, 375–378.
- **Suggested solution:** Add an explicit asset key/path to character config or
  normalize tracked folder names and every reference in one reviewed change.
- **Change risk:** Medium; case-only renames are awkward on Windows/Git.
- **Dependencies:** PF-003 asset paths/cache; cross-platform smoke test.
- **Status:** Resolved in Phase 2 with explicit case-correct `asset_dir`
  configuration and exact-case asset validation.

### PF-002 — Match navigation contradicts code comment

- **Category / severity:** Functional flow / medium
- **Affected:** `main.py` lines 397–411 and 490–495
- **Description:** Victory sets `run = False`; the next outer-loop action is
  `initial_screen()`, although the comment says “go back to selection”.
- **Impact:** Users must click Play again; future changes may rely on the wrong
  documented transition.
- **Evidence:** Direct control-flow trace.
- **Suggested solution:** First decide desired UX. Either update only the
  comment/docs or introduce explicit scene transitions in a later phase.
- **Change risk:** Low for documentation, medium for behavior.
- **Dependencies:** Scene-state work (PF-013).
- **Status:** Resolved in Phase 1 by correcting the comment to match the
  preserved return-to-menu behavior. No navigation behavior changed.

### PF-003 — CWD- and Windows-dependent paths

- **Category / severity:** Portability / high
- **Affected:** All paths in `main.py`
- **Description:** Paths use backslashes and are resolved from process CWD,
  rather than from the repository/module location.
- **Impact:** Launching from another directory fails; backslashes are not path
  separators on POSIX.
- **Evidence:** Reproduced from the parent directory: module resolution fails
  before assets load. All runtime path literals use `assets\\...`.
- **Suggested solution:** Define a `Path(__file__).resolve().parent` asset root
  and compose paths with `/`; later centralize loading.
- **Change risk:** Low-to-medium; validate every asset and packaging scenario.
- **Dependencies:** PF-001 and PF-006.
- **Status:** Resolved in Phase 2. `AssetManager` anchors `pathlib` paths to the
  repository-local asset directory; root and parent-CWD smoke checks pass.

### PF-004 — Simultaneous KO is biased

- **Category / severity:** Functional bug / high
- **Affected:** `main.py` lines 475–486
- **Description:** The `if fighter_1 dead / elif fighter_2 dead` sequence awards
  Player 2 if both are dead in the same scoring frame.
- **Impact:** Incorrect or at least undocumented round result.
- **Evidence:** Ordered mutually exclusive branch; burn makes delayed deaths
  possible, though ordinary attacks are processed sequentially.
- **Suggested solution:** Check the both-dead case first and define draw/replay
  policy.
- **Change risk:** Medium because this is a gameplay-policy decision.
- **Dependencies:** Central round resolver and tests.
- **Status:** Resolved in Phase 1. Simultaneous KO is now an explicit draw with
  no score, covered by automated tests.

### PF-005 — Importing `main` shuts Pygame down

- **Category / severity:** Architecture/testability / high
- **Affected:** `main.py` initialization and line 570
- **Description:** Pygame/display/assets initialize at import; after a non-main
  import, unconditional `pygame.quit()` invalidates the created display.
- **Impact:** Unit tests and reuse cannot safely import helpers; imports require
  a display-capable environment and mutate global process state.
- **Evidence:** Reproduced: `import main` completes but
  `main.screen.get_size()` raises `pygame.error: display Surface quit`.
- **Suggested solution:** Put startup/shutdown in `main()` and keep imports
  side-effect-light.
- **Change risk:** Medium; requires preserving current initialization order.
- **Dependencies:** PF-013; enables tests.
- **Status:** Resolved in Phase 4. Importing `main` is side-effect free; Game
  owns initialization and guaranteed shutdown.

### PF-006 — Selector reloads and re-slices images every frame

- **Category / severity:** Performance / high
- **Affected:** `main.py` lines 212–219 and 271–309
- **Description:** Two portraits and two spritesheets are loaded per selector
  frame; both idle sequences are sliced again.
- **Impact:** Avoidable disk I/O, decoding, allocations, and inconsistent
  selector performance.
- **Evidence:** Load functions are called unconditionally by per-frame drawing.
- **Suggested solution:** Load portraits and idle frames once per character or
  cache by path/configuration.
- **Change risk:** Low if output dimensions/alpha are preserved.
- **Dependencies:** PF-003 and an asset manager/cache.
- **Status:** Resolved in Phase 2. Selector assets are preloaded on entry and
  repeated access uses cached portraits, spritesheets, and idle frames.

### PF-007 — Status overlay is rebuilt pixel by pixel

- **Category / severity:** Performance / high
- **Affected:** `main.py` lines 526–559
- **Description:** Each affected frame creates a mask and scaled-cell surface,
  then runs nested Python loops over every pixel.
- **Impact:** Large frame-time spikes; scaled cells reach roughly 205–269 px per
  side, producing tens of thousands of Python iterations per frame.
- **Evidence:** Direct nested loops and allocations in battle loop.
- **Suggested solution:** Cache tinted frames or use surface blending/mask
  conversion once when image/action/frame changes.
- **Change risk:** Medium; alpha and overlay alignment must be visually checked.
- **Dependencies:** Unified status rendering and sprite cache.
- **Status:** Resolved in Phase 3. Mask overlays are cached per source
  frame/color/orientation and no Python per-pixel loop remains.

### PF-008 — Only one status overlay can render

- **Category / severity:** Functional visual bug / medium
- **Affected:** `main.py` lines 527–543
- **Description:** An `if/elif` chain selects only one of four
  player/status combinations.
- **Impact:** A second frozen/burning player has no tint; freeze takes precedence
  over burn and Player 1 precedes Player 2.
- **Evidence:** Mutually exclusive branch despite statuses existing per player.
- **Suggested solution:** Render effects independently for each Player and
  define precedence when one Player has multiple effects.
- **Change risk:** Medium; simultaneous-effect appearance needs a decision.
- **Dependencies:** PF-007 and status ownership work.
- **Status:** Resolved in Phase 3. Both effects render for both players; burn is
  drawn before freeze when they coexist on one Player.

### PF-009 — Burn is split across modules and continues after KO

- **Category / severity:** Architecture and functional risk / medium
- **Affected:** `player.py` lines 410–414; `main.py` lines 509–524
- **Description:** Player stores/starts burn, but battle code ticks it after KO
  resolution and during round-over.
- **Impact:** Ownership is hard to test; health may become negative during a
  finished round and lethal burn is scored one frame after damage.
- **Evidence:** Battle order and unconditional status block.
- **Suggested solution:** Centralize status updates, stop or explicitly allow
  ticking after round end, and clamp/apply KO in one resolver.
- **Change risk:** High because order affects match outcomes.
- **Dependencies:** PF-012, status model, round resolver.
- **Status:** Resolved in Phase 3. Player owns burn scheduling/damage and
  catches up overdue ticks; no post-round damage is applied.

### PF-010 — Dash motion ignores freeze and round-over gates

- **Category / severity:** Functional bug / high
- **Affected:** `player.py` lines 170–176
- **Description:** The dash block is outside the normal-input condition, so an
  existing dash continues while frozen, dead, or `round_over`.
- **Impact:** A fighter can slide during freeze/result and produce inconsistent
  final positions/visuals.
- **Evidence:** Direct control-flow trace.
- **Suggested solution:** Define cancellation/pausing rules and gate dash
  movement accordingly.
- **Change risk:** Medium; changes special feel and timing.
- **Dependencies:** Explicit state compatibility and dash tests.
- **Status:** Resolved in Phase 3. Freeze, death, and round end cancel dash.

### PF-011 — Dash hitbox only checks at activation

- **Category / severity:** Gameplay correctness risk / medium
- **Affected:** `player.py` lines 334–353
- **Description:** Collision and damage occur before dash travel; no collision
  is checked during its 200 ms movement.
- **Impact:** Bam can pass into/through a target without hitting unless the large
  startup rectangle already overlaps.
- **Evidence:** One `colliderect` call in `dash_attack()`; movement has none.
- **Suggested solution:** If design intends a traveling hit, define active
  frames/distance and one-hit tracking. Otherwise document the special as a
  startup-range attack.
- **Change risk:** High because balance changes.
- **Dependencies:** Combat phase/hit tracking.
- **Status:** Resolved in Phase 6. Bam's hitbox travels for the dash duration
  and one-hit tracking permits at most one collision result.

### PF-012 — Round outcome logic is duplicated and order-sensitive

- **Category / severity:** Architecture / high
- **Affected:** `main.py` timeout lines 437–448 and KO lines 475–486
- **Description:** Timeout and KO independently assign winner, score,
  `round_over`, and timestamps.
- **Impact:** Tie/simultaneous cases diverge and future scoring changes can
  update only one path.
- **Evidence:** Two separate resolution blocks in one frame.
- **Suggested solution:** One pure round-result function returning winner/reason
  and score effect.
- **Change risk:** Medium-to-high; protect with tests first.
- **Dependencies:** PF-004, PF-009, PF-018.
- **Status:** Resolved in Phase 1 with the pure `round_rules.py` resolver and
  focused tests.

### PF-013 — No centralized scene state

- **Category / severity:** Architecture / high
- **Affected:** `main.py` menu, selector, and module-level battle loop
- **Description:** Nested infinite loops and returns encode transitions.
- **Impact:** Pause, rematch, result screens, keyboard navigation, and reliable
  cleanup require cross-cutting edits.
- **Evidence:** `initial_screen()`, `character_selection_screen()`, outer loop,
  and inner battle loop each own event/frame flow.
- **Suggested solution:** Introduce a small scene enum/protocol and one
  application loop incrementally.
- **Change risk:** High if done at once; low-to-medium scene by scene.
- **Dependencies:** PF-005 and future architecture migration.
- **Status:** Resolved in Phase 4. Game owns one loop and explicit transitions
  among MenuScene, SelectionScene, BattleScene, and Quit.

### PF-014 — Broad mutable global state

- **Category / severity:** Architecture/testability / high
- **Affected:** Most of `main.py`
- **Description:** Display, assets, fonts, blink timing, countdown, score, and
  match fields are module globals; functions use globals implicitly.
- **Impact:** Hidden dependencies, difficult reset semantics, import side
  effects, and tests that interfere with each other.
- **Evidence:** global declarations and module-scope battle execution.
- **Suggested solution:** Move application/match state into a small `Game` or
  `BattleScene` object over incremental steps.
- **Change risk:** High for a bulk move; medium incrementally.
- **Dependencies:** PF-013.
- **Status:** Resolved for application/UI/match state in Phase 4. Mutable scene
  state is held by scene instances and shared runtime dependencies by
  GameContext. Player-internal flags remain for Phase 5.

### PF-015 — Player input logic is duplicated

- **Category / severity:** Maintainability / medium
- **Affected:** `player.py` lines 118–168 and attack handlers
- **Description:** Player branches duplicate block/walk/jump/attack flow and
  differ only in key mappings.
- **Impact:** New controls or input fixes can become inconsistent.
- **Evidence:** Parallel branches.
- **Suggested solution:** Pass a compact controls mapping to each Player and
  share one input path.
- **Change risk:** Medium; held-key semantics must remain unchanged initially.
- **Dependencies:** Input tests; optionally edge-trigger redesign later.
- **Status:** Resolved in Phase 5. Immutable control mappings drive one shared
  input path; parity tests cover P1/P2 movement, jump, block, and attack keys.

### PF-016 — Attacks are triggered by held keys

- **Category / severity:** Gameplay behavior/risk / medium
- **Affected:** `player.py` `move()` and attack handlers
- **Description:** Polling `get_pressed()` automatically repeats an attack after
  animation plus cooldown if its key stays held.
- **Impact:** Accidental repeats and no distinction between press and hold.
- **Evidence:** Per-frame polling; no `KEYDOWN` edge buffer.
- **Suggested solution:** Decide whether repeat is desired. If not, capture
  attack edges in scene input and queue one action.
- **Change risk:** Medium-to-high gameplay feel change.
- **Dependencies:** Controls abstraction and event ownership.

### PF-017 — Cooldowns and physics depend on frame count

- **Category / severity:** Functional/performance risk / high
- **Affected:** `player.py` movement and cooldown lines 103–201
- **Description:** Speed, gravity, and 30-step cooldown update per battle frame,
  not elapsed time. Freeze/dash/animations use milliseconds.
- **Impact:** Gameplay speed and cooldown duration change under low FPS, while
  status durations do not, causing inconsistent interactions.
- **Evidence:** Fixed increments and one decrement per `move()` call.
- **Suggested solution:** Adopt seconds/milliseconds for gameplay durations and
  delta-time movement, one subsystem at a time with baseline measurements.
- **Change risk:** High; physics feel and balance can shift.
- **Dependencies:** Stable loop and regression scenarios.
- **Status:** Partially resolved in Phase 3. Dash now uses elapsed time and
  px/s; normal movement, gravity, and attack cooldown remain frame-based.

### PF-018 — Damage is applied at animation start

- **Category / severity:** Gameplay model / medium
- **Affected:** `player.py` attack methods
- **Description:** Damage/collision resolves before attack animation advances,
  with no startup/active/recovery frames.
- **Impact:** Visual contact can disagree with hit timing; adding combos or
  character attack data is difficult.
- **Evidence:** Attack methods mutate health immediately.
- **Suggested solution:** Optional later combat phase with per-attack active
  frames and one-hit-per-activation tracking.
- **Change risk:** High gameplay/balance change.
- **Dependencies:** Animation events and configurable attack definitions.
- **Status:** Resolved in Phase 6. Explicit startup/active/recovery windows
  align collision and effects with configured animation frames.

### PF-019 — Shared body and generated attack hitboxes

- **Category / severity:** Gameplay limitation / medium
- **Affected:** `player.py` lines 22–23 and attack methods
- **Description:** Every fighter has the same 80×180 rectangle; attacks are
  width multipliers rather than character/move definitions.
- **Impact:** Visual scale does not affect collision and future characters
  cannot tune reach/height cleanly.
- **Evidence:** Hard-coded rectangle and multipliers.
- **Suggested solution:** Optional character/move hitbox config, initially with
  values reproducing the baseline.
- **Change risk:** High if baseline geometry changes.
- **Dependencies:** Combat data model and hitbox visualization tests.
- **Status:** Resolved in Phase 6. Every fighter and move has explicit
  hurtbox/attack data; initial dimensions and reach preserve baseline values.

### PF-020 — Boolean states permit incompatible combinations

- **Category / severity:** Architecture/functional risk / high
- **Affected:** `Player` combat/status fields and animation precedence
- **Description:** `attacking`, `blocking`, `hit`, `dashing`, `frozen`, and
  `burned` can overlap; cleanup is distributed across branches.
- **Impact:** Stale blocking during freeze/round end, dash during freeze, and
  hard-to-reason animation/action combinations.
- **Evidence:** Independent flags; block only refreshed inside normal input;
  freeze returns early from animation update.
- **Suggested solution:** Define a small primary action state plus orthogonal
  timed effects and explicit transition/cancellation rules.
- **Change risk:** High; migrate with tests rather than replacing all flags.
- **Dependencies:** PF-009, PF-010, PF-016.
- **Status:** Partially resolved in Phase 3. Timed records replace freeze, burn,
  and dash booleans, and dash cancellation rules are explicit. Primary
  combat/action flags remain, but Phase 5 isolated their animation precedence
  and cleanup in named methods/constants. A strict action-state model remains
  optional future work.

### PF-021 — Strict `energy == 100` issue is not present

- **Category / severity:** Verified non-issue / low
- **Affected:** `player.py` lines 224–235
- **Description:** The requested audit point has already been addressed:
  specials check `energy >= 100`, not strict equality.
- **Impact:** Over-cap energy before the next clamp cannot prevent a special.
- **Evidence:** Direct condition and upper clamp in `update()`.
- **Suggested solution:** Retain `>=`; add regression coverage when combat logic
  becomes testable.
- **Change risk:** Low.
- **Dependencies:** None.

### PF-022 — Health/energy bounds are only partially centralized

- **Category / severity:** Functional risk / medium
- **Affected:** `Player.update()` and battle burn logic
- **Description:** Upper bounds and health floor are enforced in `update()`, but
  mutations occur elsewhere and burn occurs after update. Energy has no
  explicit lower clamp.
- **Impact:** Transient out-of-range values reach later code/HUD; future costs
  could create negative energy.
- **Evidence:** Mutation sites and battle order. Current special precondition
  makes negative energy unlikely in existing flow.
- **Suggested solution:** Central mutation methods or clamp immediately in a
  tested combat resolver.
- **Change risk:** Medium due to ordering.
- **Dependencies:** PF-009 and combat tests.

### PF-023 — Timeout tie can create endless rounds

- **Category / severity:** Product-rule risk / medium
- **Affected:** `main.py` lines 438–448
- **Description:** Equal health awards no score but still restarts the round.
- **Impact:** A match can continue indefinitely if rounds repeatedly tie.
- **Evidence:** Explicit `"No One"` branch without score increment.
- **Suggested solution:** Document as current behavior and decide replay,
  double-point, sudden-death, or draw policy.
- **Change risk:** Medium gameplay policy.
- **Dependencies:** PF-012.
- **Status:** Decision documented in Phase 1: timeout ties replay without a
  point, preserving baseline behavior. Indefinitely repeated draws remain a
  deliberate rule rather than an accidental score branch.

### PF-024 — Repeated frame transforms in battle

- **Category / severity:** Performance / low
- **Affected:** `main.py` `draw_bg()` and `draw_skulls()`
- **Description:** A fixed-size background is scaled to the same size every
  frame; Player 2's skull is flipped inside the draw loop.
- **Impact:** Small, constant avoidable CPU/allocation cost.
- **Evidence:** Transform calls in per-frame functions.
- **Suggested solution:** Precompute transformed surfaces once after display
  setup.
- **Change risk:** Low.
- **Dependencies:** Asset cache.
- **Status:** Resolved in Phase 2. Fixed backgrounds are scaled once and the
  mirrored skull is created once during startup.

### PF-025 — No automated tests or dependency baseline

- **Category / severity:** Quality/maintainability / high
- **Affected:** Repository-wide
- **Description:** Baseline has no tests, pytest config, or dependency file.
- **Impact:** Combat/order regressions are difficult to detect and setup relies
  on README prose.
- **Evidence:** Full repository inventory.
- **Suggested solution:** Pin known runtime Pygame version now; extract pure
  result/stat/status logic and add small tests before risky refactors.
- **Change risk:** Low for requirements; medium when seams are introduced.
- **Dependencies:** PF-005, PF-012.
- **Status:** Resolved across Phases 0–7. Runtime and development requirements,
  pytest configuration, 103 deterministic tests, asset validation, and a
  separate headless startup check cover the documented game rules and runtime
  boundaries.

### PF-026 — README run path and badge were incorrect

- **Category / severity:** Documentation / medium
- **Affected:** `README.md`
- **Description:** Baseline command used nonexistent `src/main.py`; Python badge
  linked to Oracle/Java.
- **Impact:** New users cannot follow the documented command and receive a
  misleading link.
- **Evidence:** Repository inventory and README.
- **Suggested solution:** Use `python main.py` and link Python badge to
  python.org.
- **Change risk:** Low.
- **Dependencies:** None.

### PF-027 — Blocking wait at match victory

- **Category / severity:** Responsiveness / medium
- **Affected:** `main.py` lines 493–495
- **Description:** `pygame.time.wait(2000)` stops event processing after drawing
  victory.
- **Impact:** The window may appear unresponsive and cannot process quit during
  the two-second wait.
- **Evidence:** Blocking call inside battle loop.
- **Suggested solution:** Represent victory as a timed non-blocking result
  state.
- **Change risk:** Low-to-medium.
- **Dependencies:** PF-013.
- **Status:** Resolved in Phase 4. BattleScene uses its existing two-second
  result timer and continues processing global Quit events.

### PF-028 — `exit()` concern is not present

- **Category / severity:** Verified non-issue / low
- **Affected:** Exit paths in `main.py`
- **Description:** Current code does not call the interactive-shell `exit()`.
  It calls `pygame.quit()` and raises `SystemExit`.
- **Impact:** No action required for this specific audit concern.
- **Evidence:** Full text search/code review.
- **Suggested solution:** Preserve explicit `SystemExit` or later return cleanly
  from `main()`.
- **Change risk:** Low.
- **Dependencies:** PF-005.

### PF-029 — Asset provenance and project license are incomplete

- **Category / severity:** Distribution/legal / high
- **Affected:** Bundled assets and repository-wide source
- **Description:** Git history and README links do not map most files to exact
  product pages or retained license terms; the project source has no license.
- **Impact:** A technically valid executable can be built, but its public
  redistribution rights are not established.
- **Evidence:** Asset inventory, Git history, declared source pages, and absence
  of local license/receipt records.
- **Suggested solution:** Obtain exact source/license evidence per file and
  have the owner choose a source-code license before publishing binaries.
- **Change risk:** Low technically; legal choice requires owner authority.
- **Dependencies:** None.
- **Status:** Documented and enforced as a release gate in Phase 9.

## Architecture pressure summary

The highest-risk cluster is not code style: match resolution, timed status
effects, and overlapping Player flags share frame-order dependencies. These
should receive characterization tests before modification. Path/case fixes and
selector caching are safer early wins. A scene manager and Player refactor are
valuable but should be migrations, not a rewrite.
