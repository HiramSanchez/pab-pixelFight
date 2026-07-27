# Pending Work

This is the single source of truth for work intentionally left after the nine
improvement phases and the `src/pixel_fight` package migration. Items are not
commitments until separately approved.

## Release blockers

### P0 — Establish redistribution rights

Public binary releases remain blocked.

- Map every bundled image and `HelvetiPixel.ttf` to its exact author/product
  page.
- Retain the license text or purchase/download receipt that applied when each
  asset was obtained.
- Confirm that redistribution inside the downloadable game bundle is allowed.
- Update `THIRD_PARTY_NOTICES.md` with file-level attribution.
- Have the project owner choose and add a source-code license.

Completion means every bundled file has documented redistribution authority and
the repository contains its own license.

### P0 — Validate a clean Windows release

- Build from a fresh Windows x64 checkout using `docs/RELEASING.md`.
- Extract the generated ZIP on a machine without Python installed.
- Exercise menu, controls, selection, one complete match, pause, restart,
  selector return, menu return, and exit.
- Record the tested Windows version and artifact checksum.

Code signing is not configured, so Windows SmartScreen may still warn.

## Gameplay and timing debt

### P1 — Remove frame-rate-dependent normal physics

Walking, gravity, jumping, and the normal attack cooldown still advance per
frame, while dash and status effects use elapsed milliseconds. Migrate one
subsystem at a time with fixed 30/60/120 FPS regression scenarios so gameplay
speed remains intentional.

### P1 — Decide held-key attack behavior

Attack input uses `pygame.key.get_pressed()`. Holding an attack automatically
repeats it after animation and cooldown. Decide whether this is desired before
introducing edge-triggered input buffering.

### P1 — Strengthen Player state compatibility

`attacking`, `blocking`, `hit`, `dashing`, `frozen`, and `burned` remain
overlapping fields governed by precedence and cleanup rules. Only introduce an
explicit primary-action state model if it simplifies demonstrated invalid
combinations without changing orthogonal effects.

## Optional gameplay and experience

### P2 — Configurable controls

Control mappings are immutable Python configuration. A settings screen and
persistent bindings would require conflict validation and reset-to-default
behavior.

### P2 — Fighter body collision

Players can overlap because only screen/floor and attack collisions exist.
Adding body separation would change movement and corner behavior and therefore
needs explicit gameplay approval and tests.

### P2 — Audio

No audio was added because there are no authorized audio assets or volume
policy. Any implementation needs verified licenses, mute/volume controls, and
missing-device handling.

### P2 — Accessibility and presentation

Potential work includes clearer focus indicators, color-independent status
feedback, configurable text/volume, and updated screenshots after a visible
review.

## Maintainability candidates

### P2 — Review large modules by responsibility

`entities/player.py` and `scenes/battle.py` are intentionally still the largest
runtime modules. Do not split them solely by line count. Candidate extractions
must have a clear owner and tests—for example a stateless HUD renderer or
separate input intent—without creating generic frameworks.

### P2 — Packaged-platform support

Only Windows x64 packaging is configured. PyInstaller is not a cross-compiler;
macOS or Linux support requires native builds, platform-specific smoke tests,
and updated release documentation.

## Explicitly not planned

Unless requirements change, do not add an ECS, dependency-injection container,
event bus, networking layer, physics engine, JSON/YAML configuration system, or
class hierarchy for individual attacks/status effects.
