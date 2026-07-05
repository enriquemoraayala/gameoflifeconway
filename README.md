# Conway's Game of Life — Python + Commodore 64 BASIC V2

Two implementations of John Conway's classic **Game of Life** cellular automaton:

* A **modern HD Python** version using `pygame` + `numpy`, runnable with `uv`.
* A **retro Commodore 64** version written in **BASIC V2**, cross-compiled to `.prg` and runnable on the VICE emulator or real hardware.

---

## 📺 Preview

| Python (HD, pygame) | Commodore 64 (BASIC V2, VICE) |
| :---: | :---: |
| ![Python HD demo](assets/python_demo.gif) | ![C64 BASIC demo](assets/c64_demo.gif) |

<sub>*Drop your recorded GIFs into `assets/python_demo.gif` and `assets/c64_demo.gif` to replace the placeholders.*</sub>

Additional captures:

| Gosper Glider Gun | Pulsar | Acorn |
| :---: | :---: | :---: |
| ![Gosper](assets/gosper.gif) | ![Pulsar](assets/pulsar.gif) | ![Acorn](assets/acorn.gif) |

---

## 🧬 What is Conway's Game of Life?

The **Game of Life**, devised by mathematician **John Horton Conway in 1970**, is a zero-player cellular automaton played on a 2D grid of cells. Each cell is either **alive** or **dead**. From one generation to the next, every cell evolves in parallel based only on the state of its **8 neighbours** (Moore neighbourhood).

### The four rules

Given a live cell with `N` live neighbours:

1. **Underpopulation** — if `N < 2`, the cell dies.
2. **Survival** — if `N == 2` or `N == 3`, the cell stays alive.
3. **Overpopulation** — if `N > 3`, the cell dies.

Given a dead cell:

4. **Reproduction** — if it has exactly `N == 3` live neighbours, it becomes alive.

That's it. From these four rules emerge gliders, oscillators, guns, spaceships, and even Turing-complete computation.

Both implementations here use a **toroidal grid**: cells that leave one edge re-enter from the opposite edge.

### Included patterns

Both implementations ship with the same three built-in starting configurations. You can load any of them from the menu, or start from an empty / random grid and design your own:

* **Gosper Glider Gun** — the first known finite pattern that grows without bound, emitting a stream of gliders forever. Discovered by Bill Gosper in 1970 and worth the €50 prize Conway offered for a pattern that grew indefinitely.
* **Pulsar** — a period-3 oscillator, one of the most common naturally-occurring oscillators. Fills a 13×13 bounding box and cycles through three distinct shapes.
* **Acorn** — a 7-cell **methuselah**: it looks trivial, but takes **5206 generations** to stabilise, ending up with 633 live cells scattered across a huge area. Great to leave running.

### Starting-state options

In both versions you can decide how the simulation begins:

1. **Load a preset** — pick Gosper Glider Gun, Pulsar or Acorn from the menu. The pattern is placed centred on the grid.
2. **Custom (empty) grid** — start blank and use the cursor / mouse to paint the cells you want alive. Perfect for experimenting with your own designs (spaceships, still lifes, guns…).
3. **Random grid** — the grid is filled with a random distribution of live cells (~30% density in the Python version, uniform random in the BASIC version). Great for seeing chaotic decay into stable ecosystems.

Even after loading a preset or a random grid you remain in **edit mode** first: nothing evolves until you press `RETURN`, so you can freely add or remove cells before starting.

### Configuring the number of generations

When configuring a run, both versions ask you for a **maximum number of generations** (`GMAX`). The simulation runs until either:

* you reach `GMAX` (the run stops on the last generation and shows `FIN`), or
* you press `Q` to return to the menu.

Sensible values:

* Python: anything from `100` for a quick demo to `1_000_000` for long methuselahs like Acorn.
* C64: keep it modest — see the performance note below.

---

## 📁 Repository layout

```
gameoflifeconway/
├── README.md
├── LICENSE
├── .gitignore
├── python/
│   ├── vida_hd.py          # pygame + numpy HD implementation
│   └── pyproject.toml      # uv / pip project spec
├── basic/
│   ├── vida_final.bas      # C64 BASIC V2 — clean 38x22 grid version
│   ├── vida_charset.bas    # C64 BASIC V2 — extended version with menus, patterns, custom/random modes
│   └── prg/
│       ├── vida_final.prg  # ready-to-run C64 binary
│       └── vida_charset.prg
└── assets/                 # animated GIFs and screenshots
```

---

## 🐍 Python version (`python/vida_hd.py`)

An HD implementation designed for modern displays. Uses `numpy` for vectorised generation stepping and `pygame` for rendering.

### Features

* Grids up to **1200 × 700** cells.
* Autoscaled cell size (1–10 px) so large grids still fit on screen.
* Speed control (5–1000 generations/second, `+` / `-`).
* Interactive **editing mode**: keyboard cursor (WASD / arrows), space to toggle, mouse to paint.
* Menu-driven pattern loader (Gosper Gun, Pulsar, Acorn) or **custom / random** grids.
* Toroidal borders (matches the BASIC version's behaviour).

### Requirements

* Python **3.12** (`>=3.12,<3.13`).
* [`uv`](https://docs.astral.sh/uv/) — fast Python package/venv manager.

### Run it with `uv`

```bash
cd python

# One-off run — uv resolves and installs dependencies automatically:
uv run vida_hd.py

# Or create a persistent virtualenv:
uv sync
uv run vida_hd.py
```

If you prefer plain pip:

```bash
cd python
python3.12 -m venv .venv
source .venv/bin/activate
pip install "pygame>=2.6.1" "numpy>=2.0"
python vida_hd.py
```

### Controls

| Key | Action |
| :--- | :--- |
| `1` / `2` (menu) | Load pattern preset / custom grid |
| `WASD` or arrows | Move edit cursor |
| `SPACE` | Toggle cell under cursor |
| Left click / drag | Paint alive cells |
| Right click / drag | Erase cells |
| `RETURN` | Start simulation |
| `P` | Pause / resume |
| `+` / `-` | Faster / slower |
| `C` | Clear grid (in edit mode) |
| `R` | Randomise grid (in edit mode) |
| `Q` / `ESC` | Back to menu / quit |

---

## 🕹️ Commodore 64 version (`basic/`)

Two BASIC V2 programs written to run on a stock C64:

* **`vida_final.bas`** — minimal, clean version. Configurable grid up to 38×22, editor cursor, generation counter in the status row.
* **`vida_charset.bas`** — extended version with a start menu, built-in pattern loader (Gosper Gun / Pulsar / Acorn), custom/random modes, and character-set tweaks.

Both use PETSCII graphics on the standard 40×25 screen, direct pokes to screen RAM (`$0400`) and colour RAM (`$D800`), and a toroidal grid.

### Building the `.prg` from `.bas`

The BASIC source files are plain text. They are compiled into C64 binary `.prg` files using [`txt2prg.py`](https://github.com/enrique-mora-es-nestle/txt2prg.py) (a cross-compiler that tokenises BASIC V2 keywords and encodes PETSCII macros).

```bash
# From the repo root:
python3 /path/to/txt2prg_v2.py basic/vida_final.bas   basic/prg/vida_final.prg
python3 /path/to/txt2prg_v2.py basic/vida_charset.bas basic/prg/vida_charset.prg
```

Pre-built `.prg` files are already committed under `basic/prg/` so you can run them without recompiling.

### Running on VICE

[VICE](https://vice-emu.sourceforge.io/) is the reference Commodore 64 emulator.

**Option A — drag & drop:**

1. Launch `x64sc` (the accurate C64 emulator).
2. Drag `basic/prg/vida_final.prg` onto the emulator window.
3. It auto-loads and auto-runs.

**Option B — menu:**

1. `File → Smart-attach disk/tape/cartridge image…`
2. Pick the `.prg`.
3. Type `RUN` at the READY prompt (if it doesn't auto-run).

**Option C — command line:**

```bash
x64sc -autostart basic/prg/vida_final.prg
```

### Running on real hardware

Copy the `.prg` to an SD2IEC, 1541 Ultimate, or a real floppy, then:

```basic
LOAD "VIDA_FINAL.PRG",8,1
RUN
```

### Controls (C64)

| Key | Action |
| :--- | :--- |
| `1` / `2` (menu, charset version) | Load configuration / custom grid |
| `W A S D` or cursor keys | Move edit cursor |
| `SPACE` | Toggle cell under cursor |
| `RETURN` | Start simulation |
| `Q` | Return to menu |

The status row at the bottom of the screen shows `GEN:x/GMAX` while the simulation runs.

### ⏳ A note on real-hardware performance

The BASIC V2 interpreter on a stock 1 MHz Commodore 64 is… **slow**. Everything runs in interpreted BASIC with per-cell `POKE`s to screen and colour RAM, and each generation walks every cell to count its 8 neighbours.

In practice, with the largest grid (**38 × 22 = 836 cells**), a single generation on a real C64 (and on cycle-accurate VICE) can take **more than 30 seconds**. Small grids (10×10, 15×15) are much snappier and still very entertaining.

👉 So: load your pattern, press `RETURN`, grab a coffee ☕, and enjoy watching evolution happen at glorious 1980s speed. Patience is part of the retro experience 😉

If you want fast, high-density simulation, use the Python HD version — it happily runs thousands of generations per second on modern hardware thanks to vectorised `numpy` steps.

---

## 🔗 Related

* [`txt2prg.py`](https://github.com/enrique-mora-es-nestle/txt2prg.py) — BASIC V2 → PRG cross-compiler used to build the C64 binaries.
* [VICE emulator](https://vice-emu.sourceforge.io/) — Commodore 8-bit emulator suite.
* [LifeWiki](https://conwaylife.com/wiki/) — encyclopaedic reference for Game of Life patterns.

---

## 📜 License

MIT — see [LICENSE](LICENSE).
