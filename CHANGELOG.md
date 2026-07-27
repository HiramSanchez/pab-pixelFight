# Changelog

This project follows [Semantic Versioning](https://semver.org/). Releases are
recorded here from the first packaged preview onward.

## [Unreleased]

### Changed

- Moved runtime code into the installable `src/pixel_fight` package.
- Grouped combat, entity, resource, scene, test, screenshot, and Windows
  packaging files by responsibility.
- Consolidated dependency, package, entry-point, and pytest configuration in
  `pyproject.toml`.
- Replaced completed roadmap/audit documents with current architecture,
  gameplay, release, and pending-work documentation.

## [0.1.0] - 2026-07-26

### Added

- Deterministic round resolution and headless validation.
- Source-anchored asset loading and resource caches.
- Explicit scenes with one application loop.
- Timed burn, freeze, and dash effects.
- Configurable attack definitions and active-frame collision.
- Keyboard menu navigation, battle pause, restart, and safe scene exits.
- Windows PyInstaller build and packaged-content audit.

### Changed

- Refactored Player input, movement, animation, and combat orchestration into
  focused methods while retaining the original local two-player game.
