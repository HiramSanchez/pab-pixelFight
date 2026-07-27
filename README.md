# 🎮 Pixel Fight (pab-pixelFight)

[![Python](https://img.shields.io/badge/Python-3.13.0-blue)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6.1-green)](https://www.pygame.org/)

## 📝 Description  
**Pixel Fight** is a simple two-player fighting game inspired by retro pixel art aesthetics. The game is built using **Python** and **Pygame**, focusing on quick fights, player vs. player mechanics, and a nostalgic vibe. This is a personal project, made for having fun and understanding video game logic.

## ⚡ Features
- **2D movement**  
- **Local Multiplayer** ( 2 players on the same device )  
- **Basic Combat Mechanics** (Attack, Block, State effects)  
- **Health Bars**, **Energy Bars** and **Round Timer**  
- **Character selection**
- **Keyboard menu navigation and battle pause**

## 🛠️ Tech Used  
- Python 3.13.0  
- Pygame library (2.6.1)

Runtime code uses a conventional `src/pixel_fight` package. Combat, entities,
resources, and scenes are separated by responsibility; project tooling and
assets remain outside the runtime package.

## 🎞️ Screens 
</br>
<div>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/docs/images/screenshots/main.png" width=800>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/docs/images/screenshots/controls.png" width=397.5>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/docs/images/screenshots/selector.png" width=397.5>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/docs/images/screenshots/fight0.png" width=397.5>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/docs/images/screenshots/fight.png" width=397.5>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/docs/images/screenshots/fight3.png" width=800>
</div>
</br>

## 📦 Assets Used

The repository historically names [CraftPix](https://craftpix.net/),
[itch.io](https://itch.io/), and
[Eder Munizz](https://edermunizz.itch.io/) as sources. Exact file-to-product
provenance is incomplete, so the project does not currently claim that every
bundled file has a verified redistribution license.

See [third-party asset notices](THIRD_PARTY_NOTICES.md) for the verified font
license, unresolved provenance, and the public-release blocker.

## 🚀 Getting Started

### Run from source

Python 3.13 is the supported runtime:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pixel_fight
```

### Packaged Windows build

```powershell
python -m pip install -e ".[dev,build]"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

Extract `dist/PixelFight-windows-x64.zip`, then run `PixelFight.exe`. Python is
not required on the destination machine. Public binary publication remains
blocked until the licensing items in
[the release guide](docs/RELEASING.md) are resolved.

## ⌨️ Controls

- Menu: `W/S` or `Up/Down`, then `Enter`.
- Character selection: `W/S` for Player 1, `Up/Down` for Player 2, `Enter` to
  fight, `Escape` to return.
- Battle pause: `Escape` or `P`.
- Pause menu: `R` restart, `S` selector, `M` main menu.
- Combat controls are shown from the in-game Controls screen.

## 📚 Project Notes

- [Gameplay and runtime behavior](docs/GAMEPLAY.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Pending work](docs/PENDING_WORK.md)
- [Release process](docs/RELEASING.md)
- [Changelog](CHANGELOG.md)

## ✅ Validation

```bash
python -m pip install -e ".[dev]"
python -m compileall -q src scripts tests
python -m pytest
python scripts/validate_assets.py
python scripts/smoke_test.py
```
