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

## 🛠️ Tech Used  
- Python 3.13.0  
- Pygame library (2.6.1)

## 🎞️ Screens 
</br>
<div>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/assets/images/ss/main.png" width=800>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/assets/images/ss/controls.png" width=397.5>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/assets/images/ss/selector.png" width=397.5>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/assets/images/ss/fight0.png" width=397.5>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/assets/images/ss/fight.png" width=397.5>
<img src="https://github.com/HiramSanchez/pab-pixelFight/blob/main/assets/images/ss/fight3.png" width=800>
</div>
</br>

## 📦 Assets Used  
The game includes assets downloaded from the following sources, all under a **free license** :  

- **[Craftpix](https://craftpix.net/)** : Assets used according to their **[free license](https://craftpix.net/file-licenses/)** .
- **[Itch.io](https://itch.io/)** : Assets used following the licensing terms provided by the author.   
- **[Eder Munizz](https://edermunizz.itch.io/)** : Assets used following the licensing terms provided by the author.  

Please refer to their respective licenses for more details.

## 🚀 Getting Started

### Prerequisites  
- Make sure you have Python installed.  
- Install the runtime dependency by running:
```bash
  python -m pip install -r requirements.txt
```
### How to Run 
1. Clone this repository:  
 ```bash
   git clone https://github.com/HiramSanchez/pab-pixelFight.git
 ```
2. Run the game:
 ```bash
   python main.py
 ```

> **Current status:** Pixel Fight is playable, but its small legacy codebase is
> now being modernized incrementally. The current behavior, known technical
> risks, and planned architecture are documented before functional changes are
> made.

## 📚 Project Notes

- [Current behavior](docs/CURRENT_STATE.md)
- [Technical audit](docs/TECHNICAL_AUDIT.md)
- [Improvement roadmap](docs/IMPROVEMENT_ROADMAP.md)
- [Architecture proposal](docs/ARCHITECTURE_PROPOSAL.md)

## ✅ Validation

```bash
python -m pip install -r requirements-dev.txt
python -m py_compile main.py player.py round_rules.py asset_manager.py scripts/validate_assets.py scripts/smoke_test.py
python -m pytest
python scripts/validate_assets.py
python scripts/smoke_test.py
```

The game can be launched from the repository root with `python main.py`, or
from another working directory by passing the path to `main.py`.
